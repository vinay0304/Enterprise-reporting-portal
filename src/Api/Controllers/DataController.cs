using Microsoft.AspNetCore.Mvc;
using EnterprisePortal.Api.Services;
using Microsoft.AspNetCore.Authorization;

namespace EnterprisePortal.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class DataController : ControllerBase
{
    private readonly IReportingService _reporting;
    private readonly ILogger<DataController> _logger;

    public DataController(IReportingService reporting, ILogger<DataController> logger)
    {
        _reporting = reporting;
        _logger = logger;
    }

    [HttpGet("status")]
    public async Task<IActionResult> GetStatus()
    {
        var metrics = await _reporting.GetDashboardMetricsAsync();
        return Ok(metrics);
    }

    [HttpPost("upload")]
    [DisableRequestSizeLimit]
    public async Task<IActionResult> UploadFile(IFormFile file, [FromQuery] string sourceSystem)
    {
        if (file == null || file.Length == 0)
            return BadRequest("No file uploaded.");

        var uploadsDir = Path.Combine(Directory.GetCurrentDirectory(), "uploads");
        Directory.CreateDirectory(uploadsDir);

        var filePath = Path.Combine(uploadsDir, $"{Guid.NewGuid()}_{file.FileName}");
        using (var stream = new FileStream(filePath, FileMode.Create))
        {
            await file.CopyToAsync(stream);
        }

        // Note: In a real enterprise app, we'd trigger the Python scheduler here or queue it.
        // For this demo, we'll return a success and log it.
        _logger.LogInformation($"File {file.FileName} uploaded successfully for system {sourceSystem}. Saved to {filePath}");

        return Ok(new { Message = "File uploaded successfully.", FilePath = filePath });
    }
}
