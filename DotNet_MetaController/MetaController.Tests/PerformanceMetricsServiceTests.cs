using MetaController.API.Services;

namespace MetaController.Tests;

public class PerformanceMetricsServiceTests
{
    private readonly PerformanceMetricsService _service = new();

    [Fact]
    public void CumulativeReturn_IsPercentageChangeFromFirstToLastValue()
    {
        var values = new List<double> { 100, 105, 98, 121 };

        Assert.Equal(21.0, _service.CalculateCumulativeReturn(values), precision: 4);
    }

    [Theory]
    [InlineData(new double[] { })]
    [InlineData(new double[] { 100 })]
    public void CumulativeReturn_IsZeroWithFewerThanTwoValues(double[] values)
    {
        Assert.Equal(0.0, _service.CalculateCumulativeReturn(values.ToList()));
    }

    [Fact]
    public void MaximumDrawdown_IsWorstPeakToTroughDropInPercent()
    {
        // peak 120 -> trough 90 = 25%, larger than the earlier 110 -> 99 = 10%
        var values = new List<double> { 100, 110, 99, 120, 90, 130 };

        Assert.Equal(25.0, _service.CalculateMaximumDrawdown(values), precision: 4);
    }

    [Fact]
    public void MaximumDrawdown_IsZeroForAPortfolioThatOnlyGoesUp()
    {
        var values = new List<double> { 100, 101, 105, 110 };

        Assert.Equal(0.0, _service.CalculateMaximumDrawdown(values));
    }

    [Fact]
    public void SharpeRatio_IsAnnualisedMeanOverStandardDeviation()
    {
        var returns = new List<double> { 0.01, -0.005, 0.02, 0.0, 0.015 };
        double mean = returns.Average();
        double std = Math.Sqrt(returns.Sum(r => Math.Pow(r - mean, 2)) / returns.Count);
        double expected = Math.Round(mean / std * Math.Sqrt(252), 4);

        Assert.Equal(expected, _service.CalculateSharpeRatio(returns), precision: 4);
    }

    [Fact]
    public void SharpeRatio_SubtractsTheRiskFreeRate()
    {
        var returns = new List<double> { 0.01, -0.005, 0.02, 0.0, 0.015 };

        double withoutRiskFree = _service.CalculateSharpeRatio(returns);
        double withRiskFree = _service.CalculateSharpeRatio(returns, dailyRiskFreeRate: 0.001);

        Assert.True(withRiskFree < withoutRiskFree);
    }

    [Fact]
    public void SharpeRatio_IsZeroWhenThereIsNoVolatilityOrNoData()
    {
        Assert.Equal(0.0, _service.CalculateSharpeRatio(new List<double> { 0.25, 0.25, 0.25 }));
        Assert.Equal(0.0, _service.CalculateSharpeRatio(new List<double>()));
    }
}
