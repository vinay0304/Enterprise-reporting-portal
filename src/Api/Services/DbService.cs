using System.Data;
using Dapper;
using Microsoft.Data.SqlClient;
using EnterprisePortal.Api.Models;

namespace EnterprisePortal.Api.Services;

public interface IDbService
{
    Task<IEnumerable<T>> QueryAsync<T>(string sql, object? parameters = null);
    Task<T> QueryFirstOrDefaultAsync<T>(string sql, object? parameters = null);
    Task<int> ExecuteAsync(string sql, object? parameters = null);
    Task<int> ExecuteStoredProcedureAsync(string spName, DynamicParameters parameters);
}

public class DbService : IDbService
{
    private readonly string _connectionString;

    public DbService(IConfiguration configuration)
    {
        _connectionString = configuration.GetConnectionString("DefaultConnection")!;
    }

    private IDbConnection CreateConnection() => new SqlConnection(_connectionString);

    public async Task<IEnumerable<T>> QueryAsync<T>(string sql, object? parameters = null)
    {
        using var conn = CreateConnection();
        return await conn.QueryAsync<T>(sql, parameters);
    }

    public async Task<T> QueryFirstOrDefaultAsync<T>(string sql, object? parameters = null)
    {
        using var conn = CreateConnection();
        return await conn.QueryFirstOrDefaultAsync<T>(sql, parameters);
    }

    public async Task<int> ExecuteAsync(string sql, object? parameters = null)
    {
        using var conn = CreateConnection();
        return await conn.ExecuteAsync(sql, parameters);
    }

    public async Task<int> ExecuteStoredProcedureAsync(string spName, DynamicParameters parameters)
    {
        using var conn = CreateConnection();
        return await conn.ExecuteAsync(spName, parameters, commandType: CommandType.StoredProcedure);
    }
}
