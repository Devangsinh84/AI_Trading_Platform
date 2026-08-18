using Microsoft.AspNetCore.Mvc;
using MetaController.API.Clients;
using MetaController.API.Models;
using MetaController.API.Services; // Ensures it can see LivePortfolioState
using System.Net.Http;
using System.Threading.Tasks;
using System;
using System.Text.Json;

namespace MetaController.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TradingIntelligenceController : ControllerBase
    {
        private readonly PythonAiClient _aiClient;
        private readonly LivePortfolioState _portfolioState; // NEW: The tracker
        private static readonly HttpClient _httpClient = new HttpClient();

        // NEW: Inject the tracker into the constructor
        public TradingIntelligenceController(PythonAiClient aiClient, LivePortfolioState portfolioState)
        {
            _aiClient = aiClient;
            _portfolioState = portfolioState;
        }

        [HttpGet("live-feed")]
        public async Task<IActionResult> GetLiveMarketData()
        {
            try
            {
                var response = await _httpClient.GetAsync("http://localhost:8000/predict");
                response.EnsureSuccessStatusCode();
                
                var jsonString = await response.Content.ReadAsStringAsync();
                
                // NEW: Parse the exact price from Python and save it to memory for the metrics!
                using (JsonDocument doc = JsonDocument.Parse(jsonString))
                {
                    if (doc.RootElement.TryGetProperty("price", out JsonElement priceElement))
                    {
                        _portfolioState.AddPriceTick(priceElement.GetDouble());
                    }
                }

                // Return raw JSON straight to the React frontend
                return Content(jsonString, "application/json");
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { Error = "Failed to communicate with Python Engine.", Details = ex.Message });
            }
        }

        [HttpPost("evaluate")]
        public async Task<IActionResult> EvaluateMarket([FromBody] MarketDataRequest request)
        {
            try
            {
                var aiResponse = await _aiClient.GetMarketPredictionAsync(request);
                return Ok(aiResponse);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { Error = "Failed to communicate with Python AI Engine.", Details = ex.Message });
            }
        }
    }
}