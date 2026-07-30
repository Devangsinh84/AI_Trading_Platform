using System;
using System.Collections.Generic;
using System.Linq;

namespace MetaController.API.Services
{
    public class PerformanceMetricsService
    {
        public double CalculateSharpeRatio(List<double> dailyReturns, double dailyRiskFreeRate = 0.0)
        {
            if (dailyReturns == null || dailyReturns.Count == 0) return 0;

            // 1. Calculate Average Daily Return
            double averageReturn = dailyReturns.Average();
            double excessReturn = averageReturn - dailyRiskFreeRate;

            // 2. Calculate Standard Deviation (Volatility)
            double sumOfSquaresOfDifferences = dailyReturns.Select(val => Math.Pow(val - averageReturn, 2)).Sum();
            double standardDeviation = Math.Sqrt(sumOfSquaresOfDifferences / dailyReturns.Count);

            if (standardDeviation == 0) return 0;

            // 3. Calculate Daily Sharpe and Annualize it (252 trading days in a year)
            double dailySharpe = excessReturn / standardDeviation;
            return Math.Round(dailySharpe * Math.Sqrt(252), 4);
        }

        public double CalculateMaximumDrawdown(List<double> portfolioValues)
        {
            if (portfolioValues == null || portfolioValues.Count == 0) return 0;

            double maxDrawdown = 0;
            double peak = portfolioValues[0];

            foreach (var value in portfolioValues)
            {
                if (value > peak)
                {
                    peak = value; // New high water mark
                }
                
                double drawdown = (peak - value) / peak;
                
                if (drawdown > maxDrawdown)
                {
                    maxDrawdown = drawdown; // Record the worst drop
                }
            }

            // Return as a percentage rounded to 4 decimals
            return Math.Round(maxDrawdown * 100, 4); 
        }

        public double CalculateCumulativeReturn(List<double> portfolioValues)
        {
            if (portfolioValues == null || portfolioValues.Count < 2) return 0;

            double initialValue = portfolioValues.First();
            double finalValue = portfolioValues.Last();

            double cumulativeReturn = (finalValue - initialValue) / initialValue;

            // Return as a percentage rounded to 4 decimals
            return Math.Round(cumulativeReturn * 100, 4);
        }
    }
}