-- Database Schema for Enterprise Reporting Portal
-- Target: SQL Server

-- 1. Raw Data Staging
CREATE TABLE raw_data (
    raw_id INT IDENTITY(1,1) PRIMARY KEY,
    source_system NVARCHAR(100),
    data_payload NVARCHAR(MAX), -- JSON representation of raw input
    received_at DATETIME2 DEFAULT GETUTCDATE(),
    status NVARCHAR(50) DEFAULT 'Pending' -- Pending, Validated, Failed
);

-- 2. Validated and Transformed Data
CREATE TABLE validated_data (
    record_id INT IDENTITY(1,1) PRIMARY KEY,
    external_id NVARCHAR(100), -- ID from source system
    entity_name NVARCHAR(255),
    entity_type NVARCHAR(100),
    amount DECIMAL(18,2),
    transaction_date DATE,
    is_active BIT DEFAULT 1,
    validated_at DATETIME2 DEFAULT GETUTCDATE(),
    raw_reference_id INT FOREIGN KEY REFERENCES raw_data(raw_id)
);

-- 3. Business Errors Log
CREATE TABLE errors (
    error_id INT IDENTITY(1,1) PRIMARY KEY,
    source_file NVARCHAR(255),
    error_type NVARCHAR(100), -- DataValidation, Ingestion, API
    error_message NVARCHAR(MAX),
    failed_record_json NVARCHAR(MAX),
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    is_resolved BIT DEFAULT 0
);

-- 4. Report Generation Tracking
CREATE TABLE report_runs (
    run_id INT IDENTITY(1,1) PRIMARY KEY,
    report_name NVARCHAR(100),
    parameters NVARCHAR(MAX),
    status NVARCHAR(50), -- Queued, Running, Completed, Failed
    file_path NVARCHAR(500),
    started_at DATETIME2,
    completed_at DATETIME2,
    triggered_by NVARCHAR(100)
);

-- 5. Audit Log
CREATE TABLE audit_log (
    audit_id INT IDENTITY(1,1) PRIMARY KEY,
    table_name NVARCHAR(100),
    record_id INT,
    action_type NVARCHAR(50), -- INSERT, UPDATE, DELETE
    old_values NVARCHAR(MAX),
    new_values NVARCHAR(MAX),
    changed_by NVARCHAR(100),
    changed_at DATETIME2 DEFAULT GETUTCDATE()
);

-- Indexes for Performance
CREATE INDEX IX_ValidatedData_Date ON validated_data(transaction_date);
CREATE INDEX IX_Errors_CreatedAt ON errors(created_at);
CREATE INDEX IX_ReportRuns_Status ON report_runs(status);
GO
