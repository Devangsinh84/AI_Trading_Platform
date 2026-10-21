using MetaController.API.Services;

namespace MetaController.Tests;

public class LivePortfolioStateTests
{
    [Fact]
    public void AddPriceTick_IgnoresRepeatedIdenticalPrices()
    {
        var state = new LivePortfolioState();

        state.AddPriceTick(100);
        state.AddPriceTick(100);
        state.AddPriceTick(101);

        Assert.Equal(new List<double> { 100, 101 }, state.GetPortfolioHistory());
    }

    [Fact]
    public void GetReturnsHistory_ComputesSimpleReturnsBetweenTicks()
    {
        var state = new LivePortfolioState();
        foreach (var price in new[] { 100.0, 110.0, 99.0 })
        {
            state.AddPriceTick(price);
        }

        var returns = state.GetReturnsHistory();

        Assert.Equal(2, returns.Count);
        Assert.Equal(0.10, returns[0], precision: 10);
        Assert.Equal(-0.10, returns[1], precision: 10);
    }

    [Fact]
    public void GetPortfolioHistory_ReturnsACopyThatCallersCannotModify()
    {
        var state = new LivePortfolioState();
        state.AddPriceTick(100);

        var snapshot = state.GetPortfolioHistory();
        snapshot.Add(999);

        Assert.Single(state.GetPortfolioHistory());
    }

    [Fact]
    public async Task AddPriceTick_IsSafeUnderConcurrentWrites()
    {
        var state = new LivePortfolioState();

        // 1,000 distinct prices from parallel tasks; every one must be recorded exactly once
        await Task.WhenAll(Enumerable.Range(1, 1000)
            .Select(i => Task.Run(() => state.AddPriceTick(i))));

        var history = state.GetPortfolioHistory();
        Assert.Equal(1000, history.Count);
        Assert.Equal(1000, history.Distinct().Count());
    }
}
