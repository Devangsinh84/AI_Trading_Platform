using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using MetaController.API.Services;

var builder = WebApplication.CreateBuilder(args);

// Register the Performance Metrics Service
builder.Services.AddSingleton<PerformanceMetricsService>();

// 1. Enable CORS so Vite React (localhost:5173) can fetch data
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowReactApp", policy =>
    {
        policy.WithOrigins("http://localhost:5173")
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

var app = builder.Build();

// 2. Apply the CORS policy
app.UseCors("AllowReactApp");

// 3. Keep your existing connection check endpoint
app.MapGet("/scalar/v1", () => Results.Ok(new { status = "Connected" }));

// 4. Expose the JSON REST endpoint for the React frontend
app.MapGet("/api/trading-state", () =>
{
    var marketData = new[]
    {
        new { time = "09:30", price = 150, agent = "Bull", rsi = 45, vix = 15 },
        new { time = "10:00", price = 152, agent = "Bull", rsi = 55, vix = 14 },
        new { time = "10:30", price = 155, agent = "Bull", rsi = 65, vix = 16 },
        new { time = "11:00", price = 148, agent = "Bear", rsi = 75, vix = 25 }, 
        new { time = "11:30", price = 145, agent = "Bear", rsi = 60, vix = 28 },
        new { time = "12:00", price = 142, agent = "Bear", rsi = 40, vix = 26 },
        new { time = "12:30", price = 147, agent = "Bull", rsi = 35, vix = 18 }
    };

    var shapData = new[]
    {
        new { feature = "VIX Volatility", importance = 0.85 },
        new { feature = "RSI", importance = 0.45 },
        new { feature = "MACD", importance = 0.30 },
        new { feature = "Volume", importance = 0.15 }
    };

    return Results.Ok(new { marketData, shapData });
});

app.MapGet("/api/performance-metrics", (PerformanceMetricsService metricsService) =>
{
    // Mock historical data for testing the calculation engine
    var mockDailyReturns = new List<double> { 0.012, -0.005, 0.021, 0.003, -0.015, 0.025, 0.008 };
    var mockPortfolioValues = new List<double> { 10000, 10120, 10070, 10281, 10312, 10157, 10410, 10493 };
    var cumulativeReturn = metricsService.CalculateCumulativeReturn(mockPortfolioValues);

    // Run the calculations
    var sharpeRatio = metricsService.CalculateSharpeRatio(mockDailyReturns);
    var maxDrawdown = metricsService.CalculateMaximumDrawdown(mockPortfolioValues);

    // Return the data as JSON
    return Results.Ok(new 
    {
        SharpeRatio = sharpeRatio,
        MaximumDrawdown = maxDrawdown,
        CumulativeReturn = cumulativeReturn,
        Message = "Calculated successfully"
    });
});

app.Run();