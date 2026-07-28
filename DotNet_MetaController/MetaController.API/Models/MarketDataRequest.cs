using System.Text.Json.Serialization;

namespace MetaController.API.Models
{
    public class MarketDataRequest
    {
        [JsonPropertyName("Close")]
        public double Close { get; set; }

        [JsonPropertyName("High")]
        public double High { get; set; }

        [JsonPropertyName("Low")]
        public double Low { get; set; }

        [JsonPropertyName("Open")]
        public double Open { get; set; }

        [JsonPropertyName("Volume")]
        public double Volume { get; set; }

        [JsonPropertyName("RSI_14")]
        public double RSI_14 { get; set; }

        [JsonPropertyName("MACD_12_26_9")]
        public double MACD_12_26_9 { get; set; }

        [JsonPropertyName("MACDh_12_26_9")]
        public double MACDh_12_26_9 { get; set; }

        [JsonPropertyName("MACDs_12_26_9")]
        public double MACDs_12_26_9 { get; set; }

        [JsonPropertyName("BBL_20_2.0_2.0")]
        public double BBL_20_2_0_2_0 { get; set; }

        [JsonPropertyName("BBM_20_2.0_2.0")]
        public double BBM_20_2_0_2_0 { get; set; }

        [JsonPropertyName("BBU_20_2.0_2.0")]
        public double BBU_20_2_0_2_0 { get; set; }

        [JsonPropertyName("BBB_20_2.0_2.0")]
        public double BBB_20_2_0_2_0 { get; set; }

        [JsonPropertyName("BBP_20_2.0_2.0")]
        public double BBP_20_2_0_2_0 { get; set; }
    }
}