namespace EnterprisePortal.Api.Models;

public record ReportMetadata(int RunId, string ReportName, string Status, string? FilePath, DateTime? StartedAt, DateTime? CompletedAt);

public record DashboardMetrics(int TotalRecordsProcessed, int ActiveErrorsCount, DateTime? LastReportRunAt, int RecordsReceivedToday);

public record ErrorLogEntry(int ErrorId, string SourceFile, string ErrorType, string ErrorMessage, DateTime CreatedAt, bool IsResolved);

public record ReportRequest(string ReportName, string Parameters);
