void setup() {
  // Initialize serial communication at 9600 baud rate
  Serial.begin(9600);
  
  // Initialize the analog pin A0 as input (optional, as it is input by default)
  pinMode(A2, INPUT);
}

void loop() {
  // Read the analog value from A0 (0 - 1023)
int sensorValue = analogRead(A2);
  
  // Convert the analog value to voltage (0 - 5V)
  float voltage = sensorValue * (5.0 / 1023.0);
  
  // Print the voltage to the serial monitor
  Serial.print("A2: ");
  Serial.print(voltage);
  Serial.println(" V");
  
  // Add a small delay before the next reading
  delay(1000); // Delay for 1 second
}
