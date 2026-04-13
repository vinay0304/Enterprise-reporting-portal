using Microsoft.AspNetCore.Mvc;
using EnterprisePortal.Api.Models;
using EnterprisePortal.Api.Services;
using Microsoft.AspNetCore.Authorization;

namespace EnterprisePortal.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class ReportsController : ControllerBase
{
    private readonly IReportingService _reporting;
    private readonly ILogger<ReportsController> _logger;

    public ReportsController(IReportingService reporting, ILogger<ReportsController> logger)
    {
        _reporting = reporting;
        _logger = logger;
    }

    [HttpGet]
    public async Task<IActionResult> GetReports()
    {
        var reports = await _reporting.GetReportsAsync();
        return Ok(reports);
    }

    [HttpPost("run")]
    public async Task<IActionResult> RunReport([FromBody] ReportRequest request)
    {
        var username = User.Identity?.Name ?? "system";
        var runId = await _reporting.TriggerReportAsync(request.ReportName, request.Parameters, username);
        return Ok(new { RunId = runId, Status = "Queued" });
    }

    [HttpGet("{id}/download")]
    public async Task<IActionResult> DownloadReport(int id)
    {
        var reports = await _reporting.GetReportsAsync();
        var report = reports.FirstOrDefault(r => r.RunId == id);
        
        if (report == null || string.IsNullOrEmpty(report.FilePath))
            return NotFound("Report not found or not completed.");

        if (!System.IO.File.Exists(report.FilePath))
            return NotFound("Physical file missing on server.");

        var bytes = await System.IO.File.ReadAllBytesAsync(report.FilePath);
        return File(bytes, "application/pdf", $"Report_{id}.pdf");
    }
}
