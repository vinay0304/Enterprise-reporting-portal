using Microsoft.AspNetCore.Mvc;
using EnterprisePortal.Api.Services;
using Microsoft.AspNetCore.Authorization;

namespace EnterprisePortal.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class ErrorsController : ControllerBase
{
    private readonly IReportingService _reporting;

    public ErrorsController(IReportingService reporting)
    {
        _reporting = reporting;
    }

    [HttpGet]
    public async Task<IActionResult> GetErrors([FromQuery] int page = 1, [FromQuery] int pageSize = 10)
    {
        var errors = await _reporting.GetErrorsAsync(page, pageSize);
        return Ok(errors);
    }
}
