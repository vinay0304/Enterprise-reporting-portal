-- Stored Procedures for Data Ingestion and Validation

-- 1. Ingest Raw Data
CREATE PROCEDURE usp_IngestRawData
    @SourceSystem NVARCHAR(100),
    @DataPayload NVARCHAR(MAX),
    @RawId INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO raw_data (source_system, data_payload)
    VALUES (@SourceSystem, @DataPayload);
    
    SET @RawId = SCOPE_IDENTITY();
END;
GO

-- 2. Log Validation Error
CREATE PROCEDURE usp_LogValidationError
    @SourceFile NVARCHAR(255),
    @ErrorType NVARCHAR(100),
    @ErrorMessage NVARCHAR(MAX),
    @FailedRecordJson NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO errors (source_file, error_type, error_message, failed_record_json)
    VALUES (@SourceFile, @ErrorType, @ErrorMessage, @FailedRecordJson);
END;
GO

-- 3. Trigger Report Run
CREATE PROCEDURE usp_CreateReportRun
    @ReportName NVARCHAR(100),
    @Parameters NVARCHAR(MAX),
    @TriggeredBy NVARCHAR(100),
    @RunId INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO report_runs (report_name, parameters, status, triggered_by, started_at)
    VALUES (@ReportName, @Parameters, 'Queued', @TriggeredBy, GETUTCDATE());
    
    SET @RunId = SCOPE_IDENTITY();
END;
GO

-- 4. Update Report Status
CREATE PROCEDURE usp_UpdateReportStatus
    @RunId INT,
    @Status NVARCHAR(50),
    @FilePath NVARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE report_runs
    SET status = @Status,
        file_path = ISNULL(@FilePath, file_path),
        completed_at = CASE WHEN @Status IN ('Completed', 'Failed') THEN GETUTCDATE() ELSE NULL END
    WHERE run_id = @RunId;
END;
GO
