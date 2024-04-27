from pathlib import Path

import pandas as pd
import polars as pl
import pytest
import requests

from fusion.authentication import FusionCredentials
from fusion.fusion import Fusion
from fusion.utils import distribution_to_url


def test_rust_ok():
    from fusion import rust_ok

    assert rust_ok()


def test__get_canonical_root_url():
    from fusion.utils import _get_canonical_root_url

    some_url = "https://fusion-api.jpmorgan.com/fusion/v1/a_given_resource"
    root_url = "https://fusion-api.jpmorgan.com"
    assert root_url == _get_canonical_root_url(some_url)


def test_FusionCredentials(example_creds_dict):
    FusionCredentials.from_dict(example_creds_dict)


def test_Fusion_init(example_creds_dict):
    creds = FusionCredentials.from_dict(example_creds_dict)
    fusion = Fusion(credentials=creds)
    assert fusion

    with pytest.raises(ValueError):
        Fusion(credentials=3.141)


def test_FusionCredentials_no_pxy(example_creds_dict_no_pxy):
    FusionCredentials.from_dict(example_creds_dict_no_pxy)


def test_FusionCredentials_empty_pxy(example_creds_dict_empty_pxy):
    FusionCredentials.from_dict(example_creds_dict_empty_pxy)


def test_FusionCredentials_from_empty(example_client_id, example_client_secret, tmp_path):
    # Create an existing credentials file
    credentials_file = tmp_path / "client_credentials.json"

    creds = FusionCredentials.generate_credentials_file(
        credentials_file=str(credentials_file),
        client_id=example_client_id,
        client_secret=example_client_secret,
        proxies={},
    )

    assert creds.proxies == {}


def test_FusionCredentials_from_str(example_client_id, example_client_secret, example_http_proxy, tmp_path):
    # Create an existing credentials file
    credentials_file = tmp_path / "client_credentials.json"

    creds = FusionCredentials.generate_credentials_file(
        credentials_file=str(credentials_file),
        client_id=example_client_id,
        client_secret=example_client_secret,
        proxies=example_http_proxy,
    )

    assert creds.proxies["http"] == example_http_proxy


def test_FusionCredentials_from_http_dict(
    example_client_id, example_client_secret, example_proxy_http_dict, example_http_proxy, tmp_path
):
    # Create an existing credentials file
    credentials_file = tmp_path / "client_credentials.json"

    creds = FusionCredentials.generate_credentials_file(
        credentials_file=str(credentials_file),
        client_id=example_client_id,
        client_secret=example_client_secret,
        proxies=example_proxy_http_dict,
    )

    assert creds.proxies["http"] == example_http_proxy


def test_FusionCredentials_from_https_dict(
    example_client_id, example_client_secret, example_proxy_https_dict, example_https_proxy, tmp_path
):
    # Create an existing credentials file
    credentials_file = tmp_path / "client_credentials.json"

    creds = FusionCredentials.generate_credentials_file(
        credentials_file=str(credentials_file),
        client_id=example_client_id,
        client_secret=example_client_secret,
        proxies=example_proxy_https_dict,
    )

    assert creds.proxies["https"] == example_https_proxy


def test_FusionCredentials_from_both_dict(
    example_client_id, example_client_secret, example_proxy_both_dict, example_https_proxy, example_http_proxy, tmp_path
):
    # Create an existing credentials file
    credentials_file = tmp_path / "client_credentials.json"
    creds = FusionCredentials.generate_credentials_file(
        credentials_file=str(credentials_file),
        client_id=example_client_id,
        client_secret=example_client_secret,
        proxies=example_proxy_both_dict,
    )

    assert creds.proxies["https"] == example_https_proxy
    assert creds.proxies["http"] == example_http_proxy


def test_FusionCredentials_from_both_alt_dict(
    example_client_id,
    example_client_secret,
    example_proxy_both_alt_dict,
    example_https_proxy,
    example_http_proxy,
    tmp_path,
):
    # Create an existing credentials file
    credentials_file = tmp_path / "client_credentials.json"
    creds = FusionCredentials.generate_credentials_file(
        credentials_file=str(credentials_file),
        client_id=example_client_id,
        client_secret=example_client_secret,
        proxies=example_proxy_both_alt_dict,
    )

    assert creds.proxies["https"] == example_https_proxy
    assert creds.proxies["http"] == example_http_proxy


def test__use_catalog(example_creds_dict):
    from fusion.authentication import FusionCredentials

    creds = FusionCredentials.from_dict(example_creds_dict)
    fusion = Fusion(credentials=creds)
    def_cat = "def_cat"
    fusion.default_catalog = def_cat
    assert def_cat == fusion._use_catalog(None)
    new_cat = "new_cat"
    assert new_cat == fusion._use_catalog(new_cat)


def test_date_parsing():
    import datetime

    from fusion.utils import _normalise_dt_param

    assert _normalise_dt_param(20201212) == "2020-12-12"
    assert _normalise_dt_param("20201212") == "2020-12-12"
    assert _normalise_dt_param("2020-12-12") == "2020-12-12"
    assert _normalise_dt_param(datetime.date(2020, 12, 12)) == "2020-12-12"
    assert _normalise_dt_param(datetime.datetime(2020, 12, 12, 23, 55, 59, 342380)) == "2020-12-12"


@pytest.mark.parametrize("ref_int", [-1, 0, 1, 2])
@pytest.mark.parametrize("pluraliser", [None, "s", "es"])
def test_res_plural(ref_int, pluraliser):
    from fusion.authentication import _res_plural

    res = _res_plural(ref_int, pluraliser)
    if abs(ref_int) == 1:
        assert res == ""
    else:
        assert res == pluraliser


def test_is_json_positive(good_json):
    from fusion.authentication import _is_json

    assert _is_json(good_json)


def test_is_json_negative1(bad_json1):
    from fusion.authentication import _is_json

    assert not _is_json(bad_json1)


def test_is_json_negative2(bad_json2):
    from fusion.authentication import _is_json

    assert not _is_json(bad_json2)


def test_is_json_negative3(bad_json3):
    from fusion.authentication import _is_json

    assert not _is_json(bad_json3)


def test_is_url():
    from fusion.authentication import _is_url

    assert _is_url("https://www.google.com")
    assert _is_url("http://www.google.com/some/path?qp1=1&qp2=2")
    assert not _is_url("www.google.com")
    assert not _is_url("google.com")
    assert not _is_url("google")
    assert not _is_url("googlecom")
    assert not _is_url("googlecom.")
    assert not _is_url(3.141)


def test_fusion_class(fusion_obj):
    assert fusion_obj
    assert repr(fusion_obj)
    assert fusion_obj.default_catalog == "common"
    fusion_obj.default_catalog = "other"
    assert fusion_obj.default_catalog == "other"


def test_get_fusion_filesystem(fusion_obj):
    filesystem = fusion_obj.get_fusion_filesystem()
    assert filesystem is not None


def test__call_for_dataframe_success(requests_mock):
    # Mock the response from the API endpoint
    url = "https://fusion-api.jpmorgan.com/fusion/v1/a_given_resource"
    expected_data = {"resources": [{"id": 1, "name": "Resource 1"}, {"id": 2, "name": "Resource 2"}]}
    requests_mock.get(url, json=expected_data)

    # Create a mock session
    session = requests.Session()

    # Call the _call_for_dataframe function
    df = Fusion._call_for_dataframe(url, session)

    # Check if the dataframe is created correctly
    expected_df = pd.DataFrame(expected_data["resources"])
    pd.testing.assert_frame_equal(df, expected_df)


def test__call_for_dataframe_error(requests_mock):
    # Mock the response from the API endpoint with an error status code
    url = "https://fusion-api.jpmorgan.com/fusion/v1/a_given_resource"
    requests_mock.get(url, status_code=500)

    # Create a mock session
    session = requests.Session()

    # Call the _call_for_dataframe function and expect an exception to be raised
    with pytest.raises(requests.exceptions.HTTPError):
        Fusion._call_for_dataframe(url, session)


def test__call_for_bytes_object_success(requests_mock):
    # Mock the response from the API endpoint
    url = "https://fusion-api.jpmorgan.com/fusion/v1/a_given_resource"
    expected_data = b"some binary data"
    requests_mock.get(url, content=expected_data)

    # Create a mock session
    session = requests.Session()

    # Call the _call_for_bytes_object function
    data = Fusion._call_for_bytes_object(url, session)

    # Check if the data is returned correctly
    assert data.getbuffer() == expected_data


def test__call_for_bytes_object_fail(requests_mock):
    # Mock the response from the API endpoint with an error status code
    url = "https://fusion-api.jpmorgan.com/fusion/v1/a_given_resource"
    requests_mock.get(url, status_code=500)

    # Create a mock session
    session = requests.Session()

    # Call the _call_for_dataframe function and expect an exception to be raised
    with pytest.raises(requests.exceptions.HTTPError):
        Fusion._call_for_bytes_object(url, session)


def test_list_catalogs_success(requests_mock, fusion_obj):
    # Mock the response from the API endpoint
    url = "https://fusion-api.jpmorgan.com/fusion/v1/catalogs/"
    expected_data = {"resources": [{"id": 1, "name": "Catalog 1"}, {"id": 2, "name": "Catalog 2"}]}
    requests_mock.get(url, json=expected_data)

    # Call the list_catalogs method
    df = fusion_obj.list_catalogs()

    # Check if the dataframe is created correctly
    expected_df = pd.DataFrame(expected_data["resources"])
    pd.testing.assert_frame_equal(df, expected_df)


def test_list_catalogs_fail(requests_mock, fusion_obj):
    # Mock the response from the API endpoint with an error status code
    url = "https://fusion-api.jpmorgan.com/fusion/v1/catalogs/"
    requests_mock.get(url, status_code=500)

    # Call the list_catalogs method and expect an exception to be raised
    with pytest.raises(requests.exceptions.HTTPError):
        fusion_obj.list_catalogs()


def test_catalog_resources_success(requests_mock, fusion_obj):
    # Mock the response from the API endpoint

    new_catalog = "catalog_id"
    url = f"{fusion_obj.root_url}catalogs/{new_catalog}"
    expected_data = {"resources": [{"id": 1, "name": "Resource 1"}, {"id": 2, "name": "Resource 2"}]}
    requests_mock.get(url, json=expected_data)

    # Call the catalog_resources method
    df = fusion_obj.catalog_resources(new_catalog)

    # Check if the dataframe is created correctly
    expected_df = pd.DataFrame(expected_data["resources"])
    pd.testing.assert_frame_equal(df, expected_df)


def test_list_products_success(requests_mock, fusion_obj):
    new_catalog = "catalog_id"
    url = f"{fusion_obj.root_url}catalogs/{new_catalog}/products"
    server_mock_data = {
        "resources": [{"category": ["FX"], "region": ["US"]}, {"category": ["FX"], "region": ["US", "EU"]}]
    }
    expected_data = {"resources": [{"category": "FX", "region": "US"}, {"category": "FX", "region": "US, EU"}]}

    requests_mock.get(url, json=server_mock_data)

    # Call the catalog_resources method
    df = fusion_obj.list_products(catalog=new_catalog, max_results=2)
    # Check if the dataframe is created correctly
    expected_df = pd.DataFrame(expected_data["resources"])
    pd.testing.assert_frame_equal(df, expected_df)


def test_list_products_contains_success(requests_mock, fusion_obj):
    new_catalog = "catalog_id"
    url = f"{fusion_obj.root_url}catalogs/{new_catalog}/products"
    server_mock_data = {
        "resources": [
            {"identifier": "1", "description": "some desc", "category": ["FX"], "region": ["US"]},
            {"identifier": "2", "description": "some desc", "category": ["FX"], "region": ["US", "EU"]},
        ]
    }
    expected_data = {
        "resources": [
            {"identifier": "1", "description": "some desc", "category": "FX", "region": "US"},
        ]
    }
    expected_df = pd.DataFrame(expected_data["resources"])

    requests_mock.get(url, json=server_mock_data)

    # Call the catalog_resources method
    df = fusion_obj.list_products(catalog=new_catalog, max_results=2, contains=["1"])
    # Check if the dataframe is created correctly
    pd.testing.assert_frame_equal(df, expected_df)

    df = fusion_obj.list_products(catalog=new_catalog, max_results=2, contains="1")
    # Check if the dataframe is created correctly
    pd.testing.assert_frame_equal(df, expected_df)

    df = fusion_obj.list_products(catalog=new_catalog, max_results=2, contains="1", id_contains=True)
    # Check if the dataframe is created correctly
    pd.testing.assert_frame_equal(df, expected_df)


def test_list_datasets_success(requests_mock, fusion_obj):
    new_catalog = "catalog_id"
    url = f"{fusion_obj.root_url}catalogs/{new_catalog}/datasets"
    server_mock_data = {
        "resources": [{"category": ["FX"], "region": ["US"]}, {"category": ["FX"], "region": ["US", "EU"]}]
    }
    expected_data = {"resources": [{"region": "US", "category": "FX"}, {"region": "US, EU", "category": "FX"}]}

    requests_mock.get(url, json=server_mock_data)

    # Call the catalog_resources method
    df = fusion_obj.list_datasets(catalog=new_catalog, max_results=2)
    # Check if the dataframe is created correctly
    expected_df = pd.DataFrame(expected_data["resources"])
    pd.testing.assert_frame_equal(df, expected_df)


def test_list_datasets_contains_success(requests_mock, fusion_obj):
    new_catalog = "catalog_id"
    url = f"{fusion_obj.root_url}catalogs/{new_catalog}/datasets"
    server_mock_data = {
        "resources": [
            {"identifier": "1", "description": "some desc", "category": ["FX"], "region": ["US"], "status": "active"},
            {
                "identifier": "2",
                "description": "some desc",
                "category": ["FX"],
                "region": ["US", "EU"],
                "status": "inactive",
            },
        ]
    }
    expected_data = {
        "resources": [
            {"identifier": "1", "region": "US", "category": "FX", "description": "some desc", "status": "active"}
        ]
    }

    expected_df = pd.DataFrame(expected_data["resources"])

    requests_mock.get(url, json=server_mock_data)

    select_prod = "prod_a"
    prod_url = f"{fusion_obj.root_url}catalogs/{new_catalog}/productDatasets"
    server_prod_mock_data = {
        "resources": [
            {"product": select_prod, "dataset": "1"},
            {"product": "prod_b", "dataset": "2"},
        ]
    }
    requests_mock.get(prod_url, json=server_prod_mock_data)

    # Call the catalog_resources method
    df = fusion_obj.list_datasets(catalog=new_catalog, max_results=2, contains=["1"])
    # Check if the dataframe is created correctly
    pd.testing.assert_frame_equal(df, expected_df)

    df = fusion_obj.list_datasets(catalog=new_catalog, max_results=2, contains="1")
    # Check if the dataframe is created correctly
    pd.testing.assert_frame_equal(df, expected_df)

    df = fusion_obj.list_datasets(catalog=new_catalog, max_results=2, contains="1", id_contains=True)
    # Check if the dataframe is created correctly
    pd.testing.assert_frame_equal(df, expected_df)

    df = fusion_obj.list_datasets(catalog=new_catalog, max_results=2, product=select_prod)
    # Check if the dataframe is created correctly
    pd.testing.assert_frame_equal(df, expected_df)

    df = fusion_obj.list_datasets(catalog=new_catalog, max_results=2, status="active")
    # Check if the dataframe is created correctly
    pd.testing.assert_frame_equal(df, expected_df)


def test_dataset_resources_success(requests_mock, fusion_obj):
    new_catalog = "catalog_id"
    dataset = "my_dataset"
    url = f"{fusion_obj.root_url}catalogs/{new_catalog}/datasets/{dataset}"
    expected_data = {"resources": [{"id": 1, "name": "Resource 1"}, {"id": 2, "name": "Resource 2"}]}
    requests_mock.get(url, json=expected_data)

    # Call the catalog_resources method
    df = fusion_obj.dataset_resources(dataset, new_catalog)

    # Check if the dataframe is created correctly
    expected_df = pd.DataFrame(expected_data["resources"])
    pd.testing.assert_frame_equal(df, expected_df)


def test_list_dataset_attributes(requests_mock, fusion_obj):
    new_catalog = "catalog_id"
    dataset = "my_dataset"
    url = f"{fusion_obj.root_url}catalogs/{new_catalog}/datasets/{dataset}/attributes"

    core_cols = [
        "identifier",
        "title",
        "dataType",
        "isDatasetKey",
        "description",
        "source",
    ]

    server_mock_data = {
        "resources": [
            {
                "index": 0,
                "identifier": "attr_1",
                "title": "some title",
                "dataType": "string",
                "other_meta_attr": "some val",
                "status": "active",
            },
            {
                "index": 1,
                "identifier": "attr_2",
                "title": "some title",
                "dataType": "int",
                "other_meta_attr": "some val",
                "status": "active",
            },
        ]
    }
    expected_data = {
        "resources": [
            {
                "identifier": "attr_1",
                "title": "some title",
                "dataType": "string",
            },
            {
                "identifier": "attr_2",
                "title": "some title",
                "dataType": "int",
            },
        ]
    }

    expected_df = pd.DataFrame(expected_data["resources"])

    requests_mock.get(url, json=server_mock_data)

    # Call the catalog_resources method
    df = fusion_obj.list_dataset_attributes(dataset, catalog=new_catalog)
    # Check if the dataframe is created correctly
    pd.testing.assert_frame_equal(df, expected_df)
    assert all(col in core_cols for col in df.columns)

    ext_expected_data = {
        "resources": [
            {
                "index": 0,
                "identifier": "attr_1",
                "title": "some title",
                "dataType": "string",
                "other_meta_attr": "some val",
                "status": "active",
            },
            {
                "index": 1,
                "identifier": "attr_2",
                "title": "some title",
                "dataType": "int",
                "other_meta_attr": "some val",
                "status": "active",
            },
        ]
    }

    ext_expected_df = pd.DataFrame(ext_expected_data["resources"])
    # Call the catalog_resources method
    df = fusion_obj.list_dataset_attributes(dataset, catalog=new_catalog, display_all_columns=True)

    # Check if the dataframe is created correctly
    pd.testing.assert_frame_equal(df, ext_expected_df)


def test_list_datasetmembers_success(requests_mock, fusion_obj):
    new_catalog = "catalog_id"
    dataset = "my_dataset"
    url = f"{fusion_obj.root_url}catalogs/{new_catalog}/datasets/{dataset}/datasetseries"
    expected_data = {"resources": [{"id": 1, "name": "Resource 1"}, {"id": 2, "name": "Resource 2"}]}
    requests_mock.get(url, json=expected_data)

    # Call the catalog_resources method
    df = fusion_obj.list_datasetmembers(dataset, new_catalog, max_results=2)

    # Check if the dataframe is created correctly
    expected_df = pd.DataFrame(expected_data["resources"])
    pd.testing.assert_frame_equal(df, expected_df)


def test_datasetmember_resources_success(requests_mock, fusion_obj):
    new_catalog = "catalog_id"
    dataset = "my_dataset"
    series = "2022-02-02"
    url = f"{fusion_obj.root_url}catalogs/{new_catalog}/datasets/{dataset}/datasetseries/{series}"
    expected_data = {"resources": [{"id": 1, "name": "Resource 1"}, {"id": 2, "name": "Resource 2"}]}
    requests_mock.get(url, json=expected_data)

    # Call the catalog_resources method
    df = fusion_obj.datasetmember_resources(dataset, series, new_catalog)

    # Check if the dataframe is created correctly
    expected_df = pd.DataFrame(expected_data["resources"])
    pd.testing.assert_frame_equal(df, expected_df)


def test_list_distributions_success(requests_mock, fusion_obj):
    new_catalog = "catalog_id"
    dataset = "my_dataset"
    series = "2022-02-02"
    url = f"{fusion_obj.root_url}catalogs/{new_catalog}/datasets/{dataset}/datasetseries/{series}/distributions"
    expected_data = {"resources": [{"id": 1, "name": "Resource 1"}, {"id": 2, "name": "Resource 2"}]}
    requests_mock.get(url, json=expected_data)

    # Call the catalog_resources method
    df = fusion_obj.list_distributions(dataset, series, new_catalog)

    # Check if the dataframe is created correctly
    expected_df = pd.DataFrame(expected_data["resources"])
    pd.testing.assert_frame_equal(df, expected_df)


def test__resolve_distro_tuples(mocker, fusion_obj):
    catalog = "my_catalog"
    with (
        pytest.raises(AssertionError),
        mocker.patch.object(fusion_obj, "list_datasetmembers", return_value=pd.DataFrame()),
    ):
        fusion_obj._resolve_distro_tuples("dataset", "catalog", "series")

    valid_ds_members = pd.DataFrame(
        {
            "@id": ["2020-01-01", "2020-01-02", "2020-01-03"],
            "identifier": ["2020-01-01", "2020-01-02", "2020-01-03"],
            "dataset": ["dataset", "dataset", "dataset"],
            "createdDate": ["2020-01-01", "2020-01-02", "2020-01-03"],
        }
    )
    exp_tuples = [
        (catalog, "dataset", "2020-01-01", "parquet"),
        (catalog, "dataset", "2020-01-02", "parquet"),
        (catalog, "dataset", "2020-01-03", "parquet"),
    ]

    with (
        mocker.patch.object(fusion_obj, "list_datasetmembers", return_value=valid_ds_members),
    ):
        res = fusion_obj._resolve_distro_tuples("dataset", catalog=catalog, dt_str="2020-01-01:2020-01-03")
        assert res == exp_tuples
        res = fusion_obj._resolve_distro_tuples("dataset", catalog=catalog, dt_str=":")
        assert res == exp_tuples
        res = fusion_obj._resolve_distro_tuples("dataset", catalog=catalog, dt_str="2020-01-01:2020-01-02")
        assert res == exp_tuples[0:2]
        res = fusion_obj._resolve_distro_tuples("dataset", catalog=catalog, dt_str="2020-01-02:2020-01-03")
        assert res == exp_tuples[1:]
        res = fusion_obj._resolve_distro_tuples("dataset", catalog=catalog)
        assert res == [exp_tuples[-1]]
        res = fusion_obj._resolve_distro_tuples("dataset", catalog=catalog, dt_str="2020-01-03")
        assert res == [exp_tuples[-1]]
        res = fusion_obj._resolve_distro_tuples("dataset", catalog=catalog, dt_str="latest")
        assert res == [exp_tuples[-1]]


def test_to_bytes(requests_mock, fusion_obj):
    catalog = "my_catalog"
    dataset = "my_dataset"
    datasetseries = "2020-04-04"
    file_format = "csv"
    url = distribution_to_url(fusion_obj.root_url, catalog, dataset, datasetseries, file_format)
    expected_data = b"some binary data"
    requests_mock.get(url, content=expected_data)

    data = fusion_obj.to_bytes(catalog, dataset, datasetseries, file_format)

    # Check if the data is returned correctly
    assert data.getbuffer() == expected_data


def test_download_main(mocker, fusion_obj):
    catalog = "my_catalog"
    dataset = "my_dataset"
    dt_str = "20200101:20200103"
    file_format = "csv"

    dates = ["2020-01-01", "2020-01-02", "2020-01-03"]
    patch_res = [(catalog, dataset, dt, "parquet") for dt in dates]

    mocker.patch.object(
        fusion_obj,
        "_resolve_distro_tuples",
        return_value=patch_res,
    )

    dwn_load_res = [
        (True, f"{fusion_obj.download_folder}/{dataset}__{catalog}__{dt}.{file_format}", None) for dt in dates
    ]
    mocker.patch(
        "fusion.fusion.download_single_file_threading",
        return_value=dwn_load_res,
    )

    mocker.patch("fusion.fusion.stream_single_file_new_session", return_value=dwn_load_res[0])

    res = fusion_obj.download(dataset=dataset, dt_str=dt_str, dataset_format=file_format, catalog=catalog)
    assert not res

    res = fusion_obj.download(
        dataset=dataset, dt_str=dt_str, dataset_format=file_format, catalog=catalog, return_paths=True
    )
    assert res
    assert len(res[0]) == len(dates)

    res = fusion_obj.download(
        dataset=dataset,
        dt_str=dt_str,
        dataset_format=file_format,
        catalog=catalog,
        return_paths=True,
        show_progress=False,
    )
    assert res
    assert len(res) == len(dates)

    res = fusion_obj.download(
        dataset=dataset,
        dt_str=dt_str,
        dataset_format=file_format,
        catalog=catalog,
        return_paths=True,
        partitioning="hive",
    )
    assert res
    assert len(res) == len(dates)

    res = fusion_obj.download(
        dataset=dataset, dt_str="latest", dataset_format=file_format, catalog=catalog, return_paths=True
    )
    assert res
    assert len(res[0]) == len(dates)

    mocker.patch("fusion.fusion.stream_single_file_new_session", return_value=(False, "my_file.dat", "Some Err"))
    res = fusion_obj.download(
        dataset=dataset,
        dt_str=dt_str,
        dataset_format=file_format,
        catalog=catalog,
        return_paths=True,
        show_progress=False,
    )
    assert res
    assert len(res[0]) == len(dates)
    for r in res:
        assert not r[0]

    res = fusion_obj.download(
        dataset=dataset, dt_str="sample", dataset_format=file_format, catalog=catalog, return_paths=True
    )
    assert res
    assert len(res) == 1
    assert res[0][0]
    assert "sample" in res[0][1]


@pytest.fixture
def data_table():
    return pl.DataFrame(
        {"col_1": range(10), "col_2": [str(x) for x in range(10)], "col_3": [x / 3.14159 for x in range(10)]}
    )


@pytest.fixture
def data_table_as_csv(data_table):
    return data_table.write_csv(None)


@pytest.fixture
def data_table_as_json(data_table):
    return data_table.write_json(None)


def test_to_df(mocker, tmp_path, fusion_obj, data_table_as_csv):
    catalog = "my_catalog"
    dataset = "my_dataset"
    dates = ["2020-01-01", "2020-01-02", "2020-01-03"]

    files = [f"{tmp_path}/{dataset}__{catalog}__{dt}.csv" for dt in dates]
    for f in files:
        with Path(f).open("w") as f_h:
            f_h.write(data_table_as_csv)

    patch_res = [(True, file, None) for file in files]

    mocker.patch.object(
        fusion_obj,
        "download",
        return_value=patch_res,
    )

    res = fusion_obj.to_df(dataset, f"{dates[0]}:{dates[-1]}", "csv", catalog=catalog)
    assert len(res) > 0


def test_to_table(mocker, tmp_path, data_table_as_csv, fusion_obj):
    catalog = "my_catalog"
    dataset = "my_dataset"
    dates = ["2020-01-01", "2020-01-02", "2020-01-03"]
    format = "csv"

    files = [f"{tmp_path}/{dataset}__{catalog}__{dt}.{format}" for dt in dates]
    for f in files:
        with Path(f).open("w") as f_h:
            f_h.write(data_table_as_csv)

    patch_res = [(True, file, None) for file in files]

    mocker.patch.object(
        fusion_obj,
        "download",
        return_value=patch_res,
    )

    res = fusion_obj.to_table(dataset, f"{dates[0]}:{dates[-1]}", format, catalog=catalog)
    assert len(res) > 0
