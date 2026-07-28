using System.Net.Http.Json;
using MetaController.API.Models;

namespace MetaController.API.Clients
{
    public class PythonAiClient
    {
        private readonly HttpClient _httpClient;

        // The constructor injects the HttpClient so we don't exhaust system sockets
        public PythonAiClient(HttpClient httpClient)
        {
            _httpClient = httpClient;
            // Point this directly at your Python FastAPI server
            _httpClient.BaseAddress = new Uri("http://127.0.0.1:8000/");
        }

        public async Task<AiPredictionResponse> GetMarketPredictionAsync(MarketDataRequest marketData)
        {
            Console.WriteLine("[*] C# Client sending market data to Python AI Engine...");
            
            // Fires a POST request to the /predict endpoint you wrote in Python
            var response = await _httpClient.PostAsJsonAsync("predict", marketData);
            
            // If Python crashes or returns a 500 error, this throws a clear C# exception
            response.EnsureSuccessStatusCode();
            
            // Automatically deserialize the JSON response back into our C# object
            return await response.Content.ReadFromJsonAsync<AiPredictionResponse>();
        }
    }
}