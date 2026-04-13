using System.Diagnostics;
using EnterprisePortal.Api.Models;

namespace EnterprisePortal.Api.Services;

public class ReportQueueProcessor : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<ReportQueueProcessor> _logger;
    private readonly string _pythonPath;
    private readonly string _scriptsRoot;

    public ReportQueueProcessor(IServiceProvider serviceProvider, ILogger<ReportQueueProcessor> logger, IConfiguration configuration)
    {
        _serviceProvider = serviceProvider;
        _logger = logger;
        _pythonPath = configuration["PythonPaths:Interpreter"] ?? "python3";
        _scriptsRoot = configuration["PythonPaths:ScriptsRoot"] ?? "../Scripts";
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Report Queue Processor is starting.");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                using var scope = _serviceProvider.CreateScope();
                var db = scope.ServiceProvider.GetRequiredService<IDbService>();

                // Check for Queued reports
                var queuedReports = await db.QueryAsync<ReportQueueJob>(
                    "SELECT TOP 5 run_id as RunId FROM report_runs WHERE status = 'Queued'");

                foreach (var report in queuedReports)
                {
                    _logger.LogInformation($"Processing report job: {report.RunId}");
                    await RunPythonGenerator(report.RunId);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in Report Queue Processor");
            }

            await Task.Delay( TimeSpan.FromSeconds(10), stoppingToken);
        }
    }

    private async Task RunPythonGenerator(int runId)
    {
        var scriptPath = Path.Combine(_scriptsRoot, "report_generator.py");
        var psi = new ProcessStartInfo
        {
            FileName = _pythonPath,
            Arguments = $"{scriptPath} --run_id {runId}",
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        try
        {
            using var process = Process.Start(psi);
            if (process != null)
            {
                var output = await process.StandardOutput.ReadToEndAsync();
                var error = await process.StandardError.ReadToEndAsync();
                await process.WaitForExitAsync();

                if (process.ExitCode != 0)
                {
                    _logger.LogError($"Python report generator failed for RunId {runId}. Error: {error}");
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Failed to start report generator for RunId {runId}");
        }
    }
}
