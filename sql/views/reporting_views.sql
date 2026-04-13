-- Views for Dashboard and Reporting

-- 1. Dashboard Metrics
CREATE VIEW vw_DashboardMetrics AS
SELECT 
    (SELECT COUNT(*) FROM validated_data) AS total_records_processed,
    (SELECT COUNT(*) FROM errors WHERE is_resolved = 0) AS active_errors_count,
    (SELECT MAX(completed_at) FROM report_runs WHERE status = 'Completed') AS last_report_run_at,
    (SELECT COUNT(*) FROM raw_data WHERE CAST(received_at AS DATE) = CAST(GETUTCDATE() AS DATE)) AS records_received_today;
GO

-- 2. Error Breakdown View
CREATE VIEW vw_ErrorLog AS
SELECT 
    error_id,
    source_file,
    error_type,
    error_message,
    created_at,
    is_resolved
FROM errors;
GO

-- 3. Report Status View
CREATE VIEW vw_ReportStatus AS
SELECT 
    run_id,
    report_name,
    status,
    triggered_by,
    started_at,
    completed_at,
    DATEDIFF(SECOND, started_at, completed_at) AS duration_seconds
FROM report_runs;
GO
