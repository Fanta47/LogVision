from elasticsearch import Elasticsearch
import pandas as pd
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

es = Elasticsearch(
    "https://localhost:9201",
    basic_auth=("elastic", "changeme123"),
    verify_certs=False
)

INDEX_NAME = "log-unified-*"
BATCH_SIZE = 1000

timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M")

COMMON_COLUMNS = [
    "@timestamp",
    "application_name",
    "log_level",
    "log_origin",
    "thread",
    "context",
    "details",
    "log_family",
    "event_type",
    "source_file",
    "analysis_status"
]

SQL_COLUMNS = [
    "@timestamp",
    "application_name",
    "log_level",
    "log_origin",
    "thread",
    "context",
    "log_family",
    "event_type",
    "query_stage",
    "query_text",
    "sql_operation",
    "sql_table",
    "query_has_placeholders",
    "main_entity_id",
    "sql_entity_family",
    "result_size",
    "update_count",
    "data_source",
    "source_file",
    "analysis_status"
]

SCHEDULER_COLUMNS = [
    "@timestamp",
    "application_name",
    "log_level",
    "log_origin",
    "thread",
    "worker_id",
    "context",
    "log_family",
    "event_type",
    "criterion",
    "controller_name",
    "method_name",
    "method_display_name",
    "service_domain",
    "source_file",
    "analysis_status"
]

ERROR_COLUMNS = [
    "@timestamp",
    "application_name",
    "log_level",
    "log_origin",
    "thread",
    "context",
    "log_family",
    "event_type",
    "error_message",
    "exception_class",
    "root_exception_class",
    "error_keyword",
    "caused_by_count",
    "stack_trace",
    "source_file",
    "analysis_status"
]


def fetch_all_documents(index_name: str) -> list[dict]:
    response = es.search(
        index=index_name,
        scroll="2m",
        size=BATCH_SIZE,
        query={"match_all": {}}
    )

    scroll_id = response["_scroll_id"]
    hits = response["hits"]["hits"]

    rows = []
    while hits:
        for hit in hits:
            rows.append(hit["_source"])

        response = es.scroll(scroll_id=scroll_id, scroll="2m")
        scroll_id = response["_scroll_id"]
        hits = response["hits"]["hits"]

    return rows


def ensure_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    return df[columns].fillna("")


def save_csv(df: pd.DataFrame, filename: str) -> None:
    df.to_csv(filename, index=False, sep=";", encoding="utf-8-sig")
    print(f"Created: {filename} | rows={len(df)} | cols={len(df.columns)}")


def derive_extra_fields(df: pd.DataFrame) -> pd.DataFrame:
    if "controller_name" in df.columns:
        df["service_domain"] = df["service_domain"].replace("", pd.NA)
        missing_mask = df["service_domain"].isna() & df["controller_name"].notna()
        df.loc[missing_mask, "service_domain"] = (
            df.loc[missing_mask, "controller_name"]
              .str.extract(r"com\.vermeg\.services\.([^.]+)\.ctrl", expand=False)
              .fillna("")
        )

    if "thread" in df.columns:
        df["worker_id"] = df["worker_id"].replace("", pd.NA)
        missing_mask = df["worker_id"].isna() & df["thread"].notna()
        df.loc[missing_mask, "worker_id"] = (
            df.loc[missing_mask, "thread"]
              .str.extract(r"Worker-(\d+)", expand=False)
              .fillna("")
        )

    if "stack_trace" in df.columns:
        if "caused_by_count" not in df.columns:
            df["caused_by_count"] = ""
        missing_mask = (df["caused_by_count"] == "") & df["stack_trace"].notna()
        df.loc[missing_mask, "caused_by_count"] = (
            df.loc[missing_mask, "stack_trace"]
              .astype(str)
              .str.count(r"Caused by:")
              .astype(str)
        )

    if "error_keyword" in df.columns and "error_message" in df.columns:
        missing_mask = (df["error_keyword"] == "") & df["error_message"].notna()
        error_series = df.loc[missing_mask, "error_message"].astype(str)

        df.loc[missing_mask & error_series.str.contains("well-formed document", case=False, na=False), "error_keyword"] = "xml_parsing_error"
        df.loc[missing_mask & error_series.str.contains("timeout", case=False, na=False), "error_keyword"] = "timeout_error"
        df.loc[missing_mask & error_series.str.contains("database", case=False, na=False), "error_keyword"] = "database_error"
        df.loc[missing_mask & error_series.str.contains("security", case=False, na=False), "error_keyword"] = "security_error"

    return df.fillna("")


def main():
    rows = fetch_all_documents(INDEX_NAME)

    if not rows:
        print("No documents found in Elasticsearch.")
        return

    df = pd.DataFrame(rows)
    df = derive_extra_fields(df)

    # Dataset global
    base_df = ensure_columns(df.copy(), COMMON_COLUMNS)
    save_csv(base_df, f"base_event_dataset_{timestamp_str}.csv")

    # Dataset SQL
    sql_df = df[df["log_family"].astype(str).eq("sql_persistence")].copy() if "log_family" in df.columns else pd.DataFrame()
    if not sql_df.empty:
        sql_df = ensure_columns(sql_df, SQL_COLUMNS)
        save_csv(sql_df, f"sql_dataset_{timestamp_str}.csv")
    else:
        print("No SQL rows found.")

    # Dataset scheduler/controller
    scheduler_mask = pd.Series(False, index=df.index)
    if "log_family" in df.columns:
        scheduler_mask = df["log_family"].astype(str).isin(["scheduler_controller", "criterion_trace"])
    scheduler_df = df[scheduler_mask].copy()
    if not scheduler_df.empty:
        scheduler_df = ensure_columns(scheduler_df, SCHEDULER_COLUMNS)
        save_csv(scheduler_df, f"scheduler_controller_dataset_{timestamp_str}.csv")
    else:
        print("No scheduler/controller rows found.")

    # Dataset errors
    error_df = df[df["log_family"].astype(str).eq("application_error")].copy() if "log_family" in df.columns else pd.DataFrame()
    if not error_df.empty:
        error_df = ensure_columns(error_df, ERROR_COLUMNS)
        save_csv(error_df, f"error_dataset_{timestamp_str}.csv")
    else:
        print("No error rows found.")

    print("\nExport finished.")


if __name__ == "__main__":
    main()