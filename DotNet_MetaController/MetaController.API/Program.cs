using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.Linq;
using MetaController.API.Services;
using MetaController.API.Clients;

var builder = WebApplication.CreateBuilder(args);

// 1. Register Services
builder.Services.AddSingleton<PerformanceMetricsService>();
builder.Services.AddHttpClient<PythonAiClient>();

// 2. Register the In-Memory State Tracker
builder.Services.AddSingleton<LivePortfolioState>();

// 3. Enable CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowReactApp", policy =>
    {
        policy.WithOrigins("http://localhost:5173")
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

builder.Services.AddControllers();

var app = builder.Build();
app.UseCors("AllowReactApp");

app.MapGet("/scalar/v1", () => Results.Ok(new { status = "Connected" }));

// 4. LIVE Performance Metrics Endpoint (Dynamic Math)
app.MapGet("/api/performance-metrics", (PerformanceMetricsService metricsService, LivePortfolioState state) =>
{
    var portfolioValues = state.GetPortfolioHistory();
    var dailyReturns = state.GetReturnsHistory();

    if (portfolioValues.Count < 2)
    {
        return Results.Ok(new 
        {
            SharpeRatio = 0.0,
            MaximumDrawdown = 0.0,
            CumulativeReturn = 0.0,
            Message = "Awaiting more data ticks..."
        });
    }

    var cumulativeReturn = metricsService.CalculateCumulativeReturn(portfolioValues);
    var sharpeRatio = metricsService.CalculateSharpeRatio(dailyReturns);
    var maxDrawdown = metricsService.CalculateMaximumDrawdown(portfolioValues);

    return Results.Ok(new 
    {
        SharpeRatio = Math.Round(sharpeRatio, 4),
        MaximumDrawdown = Math.Round(maxDrawdown, 4),
        CumulativeReturn = Math.Round(cumulativeReturn, 4),
        Message = "Live calculations active"
    });
});

app.MapControllers();
app.Run();

// ==========================================
// LIVE IN-MEMORY STATE TRACKER
// ==========================================
namespace MetaController.API.Services
{
    public class LivePortfolioState
    {
        private readonly List<double> _prices = new();
        private readonly object _lock = new();

        public void AddPriceTick(double currentPrice)
        {
            lock (_lock)
            {
                if (_prices.Count == 0 || _prices.Last() != currentPrice)
                {
                    _prices.Add(currentPrice);
                }
            }
        }

        public List<double> GetPortfolioHistory()
        {
            lock (_lock)
            {
                return _prices.ToList();
            }
        }

        public List<double> GetReturnsHistory()
        {
            lock (_lock)
            {
                var returns = new List<double>();
                for (int i = 1; i < _prices.Count; i++)
                {
                    double prev = _prices[i - 1];
                    returns.Add((_prices[i] - prev) / prev);
                }
                return returns;
            }
        }
    }
}