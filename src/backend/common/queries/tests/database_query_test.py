from typing import Any, Generator, Iterable, List, TypedDict

from google.appengine.ext import ndb
from pyre_extensions import none_throws

from backend.common.consts.api_version import ApiMajorVersion
from backend.common.models.cached_query_result import CachedQueryResult
from backend.common.queries.database_query import CachedDatabaseQuery, DatabaseQuery
from backend.common.queries.dict_converters.converter_base import ConverterBase


class DummyModel(ndb.Model):
    int_prop = ndb.IntegerProperty()


class DummyDict(TypedDict):
    int_val: int


class DummyConverter(ConverterBase):
    SUBVERSIONS = {
        ApiMajorVersion.API_V3: 0,
    }

    @classmethod
    def _convert_list(
        cls, model_list: List[DummyModel], version: ApiMajorVersion
    ) -> List[DummyDict]:
        return list(map(cls.converter_v3, model_list))

    @classmethod
    def converter_v3(cls, model: DummyModel) -> DummyDict:
        return {
            "int_val": model.int_prop,
        }


class DummyModelPointQuery(DatabaseQuery[DummyModel, DummyDict]):
    DICT_CONVERTER = DummyConverter

    @ndb.tasklet
    def _query_async(self, model_key: str) -> Generator[Any, Any, DummyModel]:
        model: DummyModel = yield DummyModel.get_by_id_async(model_key)
        return model


class DummyModelRangeQuery(DatabaseQuery[List[DummyModel], List[DummyDict]]):
    DICT_CONVERTER = DummyConverter

    @ndb.tasklet
    def _query_async(self, min: int, max: int) -> Generator[Any, Any, List[DummyModel]]:
        models: Iterable[DummyModel] = yield DummyModel.query(
            DummyModel.int_prop >= min, DummyModel.int_prop <= max
        ).fetch_async()
        return list(models)


class CachedDummyModelRangeQuery(
    CachedDatabaseQuery[List[DummyModel], List[DummyDict]]
):
    CACKE_KEY_FORMAT = "test_query_{min}_{max}"
    DICT_CONVERTER = DummyConverter
    CACHE_WRITES_ENABLED = True

    @ndb.tasklet
    def _query_async(self, min: int, max: int) -> Generator[Any, Any, List[DummyModel]]:
        models: Iterable[DummyModel] = yield DummyModel.query(
            DummyModel.int_prop >= min, DummyModel.int_prop <= max
        ).fetch_async()
        return list(models)


def test_point_query_exists_sync() -> None:
    m = DummyModel(id="test")
    m.put()

    query = DummyModelPointQuery(model_key="test")
    result = query.fetch()
    assert result == m

    result_dict = query.fetch_dict(ApiMajorVersion.API_V3)
    assert result_dict == DummyConverter.converter_v3(m)


def test_point_query_not_exists_sync() -> None:
    query = DummyModelPointQuery(model_key="test")
    result = query.fetch()
    assert result is None

    result_dict = query.fetch_dict(ApiMajorVersion.API_V3)
    assert result_dict is None


def test_point_query_exists_async() -> None:
    m = DummyModel(id="test")
    m.put()

    query = DummyModelPointQuery(model_key="test")
    result_future = query.fetch_async()

    result = result_future.get_result()
    assert result == m

    result_dict = query.fetch_dict_async(ApiMajorVersion.API_V3).get_result()
    assert result_dict == DummyConverter.converter_v3(m)


def test_point_query_not_exists_async() -> None:
    query = DummyModelPointQuery(model_key="test")
    result_future = query.fetch_async()

    result = result_future.get_result()
    assert result is None

    result_dict = query.fetch_dict_async(ApiMajorVersion.API_V3).get_result()
    assert result_dict is None


def test_range_query_empty_sync() -> None:
    query = DummyModelRangeQuery(min=0, max=10)

    result = query.fetch()
    assert result == []

    result_dict = query.fetch_dict(ApiMajorVersion.API_V3)
    assert result_dict == []


def test_range_query_empty_async() -> None:
    query = DummyModelRangeQuery(min=0, max=10)

    result_future = query.fetch_async()
    result = result_future.get_result()
    assert result == []

    result_dict_future = query.fetch_dict_async(ApiMajorVersion.API_V3)
    result_dict = result_dict_future.get_result()
    assert result_dict == []


def test_range_query_with_data_sync() -> None:
    keys = ndb.put_multi([DummyModel(id=f"{i}", int_prop=i) for i in range(0, 5)])
    assert len(keys) == 5

    query = DummyModelRangeQuery(min=0, max=2)
    result = query.fetch()
    assert len(result) == 3

    result_dict = query.fetch_dict(ApiMajorVersion.API_V3)
    assert len(result_dict) == 3


def test_range_query_with_data_async() -> None:
    keys = ndb.put_multi([DummyModel(id=f"{i}", int_prop=i) for i in range(0, 5)])
    assert len(keys) == 5

    query = DummyModelRangeQuery(min=0, max=2)
    result_future = query.fetch_async()
    result = result_future.get_result()
    assert len(result) == 3

    result_dict_future = query.fetch_dict_async(ApiMajorVersion.API_V3)
    result_dict = result_dict_future.get_result()
    assert len(result_dict) == 3


def test_cached_query() -> None:
    keys = ndb.put_multi([DummyModel(id=f"{i}", int_prop=i) for i in range(0, 5)])
    assert len(keys) == 5

    query = CachedDummyModelRangeQuery(min=0, max=2)
    result = query.fetch()
    assert len(result) == 3

    # Now, verify the cached response exists
    cached_result = CachedQueryResult.get_by_id(query.cache_key)
    assert cached_result is not None

    # Verify the correct fields are written
    assert cached_result.result is not None
    assert cached_result.result_dict is None

    # And if we delete the underlying data out without clearing the cache, we should
    # still read a stale value
    [k.delete() for k in keys]
    assert ndb.get_multi(keys) == [None] * 5
    assert CachedQueryResult.get_by_id(query.cache_key) is not None

    query = CachedDummyModelRangeQuery(min=0, max=2)
    result = query.fetch()
    assert len(result) == 3


def test_cached_dict_query() -> None:
    keys = ndb.put_multi([DummyModel(id=f"{i}", int_prop=i) for i in range(0, 5)])
    assert len(keys) == 5

    query = CachedDummyModelRangeQuery(min=0, max=2)
    result = query.fetch_dict(ApiMajorVersion.API_V3)
    assert len(result) == 3

    # Now, verify the cached response exists
    cache_key = query.dict_cache_key(ApiMajorVersion.API_V3)
    cached_result = CachedQueryResult.get_by_id(cache_key)

    # Verify the correct fields are written
    assert none_throws(cached_result).result is None
    assert none_throws(cached_result).result_dict is not None

    # And if we delete the underlying data out without clearing the cache, we should
    # still read a stale value
    [k.delete() for k in keys]
    assert ndb.get_multi(keys) == [None] * 5
    assert CachedQueryResult.get_by_id(cache_key) is not None

    query = CachedDummyModelRangeQuery(min=0, max=2)
    result = query.fetch_dict(ApiMajorVersion.API_V3)
    assert len(result) == 3


def test_clear_cache() -> None:
    keys = ndb.put_multi([DummyModel(id=f"{i}", int_prop=i) for i in range(0, 5)])
    assert len(keys) == 5

    query = CachedDummyModelRangeQuery(min=0, max=2)
    result = query.fetch()
    dict_result = query.fetch_dict(ApiMajorVersion.API_V3)
    assert len(result) == 3
    assert len(dict_result) == 3

    # Now, verify the cached response exists
    cache_key = query.cache_key
    dict_cache_key = query.dict_cache_key(ApiMajorVersion.API_V3)
    assert CachedQueryResult.get_by_id(cache_key) is not None
    assert CachedQueryResult.get_by_id(dict_cache_key) is not None

    # Deleting cache for these queries should leave no CachedQueryResults remaining
    CachedDummyModelRangeQuery.delete_cache_multi({cache_key})
    assert len(CachedQueryResult.query().fetch()) == 0
