-- Sample Seed Data for Enterprise Reporting Portal

-- 1. Insert Sample Raw Data
INSERT INTO raw_data (source_system, data_payload, status)
VALUES 
('ERP_MAIN', '{"id": "TRX-001", "entity": "Global Tech", "total": 5000.00, "date": "2024-03-20"}', 'Validated'),
('LEGACY_SYS', '{"id": "TRX-002", "entity": "Aqua Corp", "total": 1250.50, "date": "2024-03-21"}', 'Validated'),
('WEBSITE', '{"id": "TRX-003", "entity": "Unknown", "total": -10.00, "date": "2024-03-22"}', 'Failed');

-- 2. Insert Sample Validated Data
INSERT INTO validated_data (external_id, entity_name, entity_type, amount, transaction_date, raw_reference_id)
VALUES 
('TRX-001', 'Global Tech', 'Enterprise', 5000.00, '2024-03-20', 1),
('TRX-002', 'Aqua Corp', 'SME', 1250.50, '2024-03-21', 2);

-- 3. Insert Sample Error
INSERT INTO errors (source_file, error_type, error_message, failed_record_json)
VALUES 
('upload_20240322.csv', 'DataValidation', 'Amount cannot be negative', '{"id": "TRX-003", "entity": "Unknown", "total": -10.00, "date": "2024-03-22"}');

-- 4. Insert Sample Report Run
INSERT INTO report_runs (report_name, parameters, status, triggered_by, started_at, completed_at)
VALUES 
('Quarterly Sales Report', '{"year": 2024, "q": 1}', 'Completed', 'admin@enterprise.com', '2024-03-01 09:00:00', '2024-03-01 09:05:22');
GO
