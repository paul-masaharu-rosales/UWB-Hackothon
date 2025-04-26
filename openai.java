import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

public class openai {

    public static void main(String[] args) {
        String apiKey = "AIzaSyAZgjoeoA8PwdBZ7UTGKqNqCBdm9V3Z9es";
        String endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + apiKey;
        String prompt = "give a number between 1 and 20";

        try {
            URL url = new URL(endpoint);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);

            String jsonInput = "{\n" +
                    "  \"contents\": [\n" +
                    "    {\n" +
                    "      \"parts\": [\n" +
                    "        {\"text\": \"" + prompt + "\"}\n" +
                    "      ]\n" +
                    "    }\n" +
                    "  ]\n" +
                    "}";

            try (OutputStream os = connection.getOutputStream()) {
                byte[] input = jsonInput.getBytes("utf-8");
                os.write(input, 0, input.length);
            }

            Scanner scanner = new Scanner(connection.getInputStream());
            String response = scanner.useDelimiter("\\A").next();
            int position1 = response.indexOf("\"text\":");
            int position2 = response.indexOf("""
                    }
        ],
        "role":
                    """);
            System.out.println(position1 + " " + position2);
            scanner.close();

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}