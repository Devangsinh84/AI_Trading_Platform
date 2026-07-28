using Microsoft.AspNetCore.Mvc;
using MetaController.API.Clients;
using MetaController.API.Models;

namespace MetaController.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TradingIntelligenceController : ControllerBase
    {
        private readonly PythonAiClient _aiClient;

        // Dependency Injection automatically provides the client we registered in Program.cs
        public TradingIntelligenceController(PythonAiClient aiClient)
        {
            _aiClient = aiClient;
        }

        [HttpPost("evaluate")]
        public async Task<IActionResult> EvaluateMarket([FromBody] MarketDataRequest request)
        {
            try
            {
                Console.WriteLine("[*] API Hit: Received market data. Routing to Python AI Engine...");
                
                // The bridge in action: C# calls Python
                var aiResponse = await _aiClient.GetMarketPredictionAsync(request);
                
                Console.WriteLine($"[+] AI Response Received: {aiResponse.Signal}");
                return Ok(aiResponse);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[!] Error bridging to Python: {ex.Message}");
                return StatusCode(500, new { Error = "Failed to communicate with Python AI Engine.", Details = ex.Message });
            }
        }
    }
}