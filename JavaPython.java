import java.io.*;
    public class JavaPython {
        public static void main(String[] args) {
            try {
                String command = "python3 openai.py";
                Process process = Runtime.getRuntime().exec(command);
                
                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println(line);
                }
                
                int exitCode = process.waitFor();
                System.out.println("\nExited with error code : " + exitCode);
            } catch (IOException |InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
