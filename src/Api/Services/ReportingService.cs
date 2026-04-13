using System.Diagnostics;
using Dapper;
using EnterprisePortal.Api.Models;

namespace EnterprisePortal.Api.Services;

public interface IReportingService
{
    Task<int> TriggerReportAsync(string reportName, string parameters, string username);
    Task<IEnumerable<ReportMetadata>> GetReportsAsync();
    Task<DashboardMetrics> GetDashboardMetricsAsync();
    Task<IEnumerable<ErrorLogEntry>> GetErrorsAsync(int page, int pageSize);
}

public class ReportingService : IReportingService
{
    private readonly IDbService _db;
    
    public ReportingService(IDbService db)
    {
        _db = db;
    }

    public async Task<int> TriggerReportAsync(string reportName, string parameters, string username)
    {
        var dynParams = new DynamicParameters();
        dynParams.Add("@ReportName", reportName);
        dynParams.Add("@Parameters", parameters);
        dynParams.Add("@TriggeredBy", username);
        dynParams.Add("@RunId", dbType: System.Data.DbType.Int32, direction: System.Data.ParameterDirection.Output);

        await _db.ExecuteStoredProcedureAsync("usp_CreateReportRun", dynParams);
        return dynParams.Get<int>("@RunId");
    }

    public async Task<IEnumerable<ReportMetadata>> GetReportsAsync()
    {
        return await _db.QueryAsync<ReportMetadata>("SELECT * FROM vw_ReportStatus ORDER BY started_at DESC");
    }

    public async Task<DashboardMetrics> GetDashboardMetricsAsync()
    {
        return await _db.QueryFirstOrDefaultAsync<DashboardMetrics>("SELECT * FROM vw_DashboardMetrics");
    }

    public async Task<IEnumerable<ErrorLogEntry>> GetErrorsAsync(int page, int pageSize)
    {
        var offset = (page - 1) * pageSize;
        return await _db.QueryAsync<ErrorLogEntry>(
            "SELECT * FROM vw_ErrorLog ORDER BY created_at DESC OFFSET @Offset ROWS FETCH NEXT @PageSize ROWS ONLY",
            new { Offset = offset, PageSize = pageSize });
    }
}
