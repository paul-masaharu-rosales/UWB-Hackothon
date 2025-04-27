import json
import os
import logging
from openai import OpenAI
import google.generativeai as genai

# Configure Google GenerativeAI
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Also keep OpenAI for other features
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def generate_anonymous_recovery(symptom, severity, description, age=None, gender=None):
    """
    Generate anonymous recovery suggestions for a single symptom without requiring user login
    Using Google's Gemini 2.0 Flash model
    """
    try:
        # Create the prompt for Gemini
        prompt = f"""
        As a medical AI assistant, generate recovery suggestions for a patient with the following symptom:
        
        Symptom: {symptom}
        Severity (1-10): {severity}
        Description: {description if description else 'Not provided'}
        
        Additional information:
        Age: {age if age else 'Not provided'}
        Gender: {gender if gender else 'Not provided'}
        
        Generate practical recovery suggestions without requiring medical supervision.
        
        Return the response in the following JSON format:
        {{
            "title": "Recovery Suggestions Title",
            "description": "Overall description of the suggestions",
            "recommendations": [
                {{
                    "title": "Recommendation Title",
                    "description": "Detailed explanation",
                    "type": "self-care, lifestyle, or home-remedy",
                    "priority": priority level (1-3, where 1 is highest priority)
                }}
            ]
        }}
        
        Provide at least 4-5 recommendations. Focus on evidence-based approaches that can be done safely at home.
        Do not suggest specific medications by name. Include clear warnings about when to seek professional medical help.
        
        Important: Format the response as valid JSON.
        """
        
        # Check if Google API key is available
        if not GOOGLE_API_KEY:
            logging.error("Google API key is not available")
            # Return a fallback response for demonstration purposes
            return {
                "title": f"Recovery Suggestions for {symptom}",
                "description": "Here are some general suggestions that may help with your symptoms. Please consult a healthcare professional for personalized advice.",
                "recommendations": [
                    {
                        "title": "Rest and Monitor",
                        "description": "Give your body time to heal by getting adequate rest. Monitor your symptoms and seek medical attention if they worsen or persist.",
                        "type": "self-care",
                        "priority": 1
                    },
                    {
                        "title": "Stay Hydrated",
                        "description": "Drink plenty of fluids to help your body recover. Water, herbal teas, and clear broths can be beneficial.",
                        "type": "lifestyle",
                        "priority": 2
                    },
                    {
                        "title": "Apply Hot/Cold Therapy",
                        "description": "For muscle or joint pain, apply heat or cold packs to the affected area for 15-20 minutes at a time.",
                        "type": "home-remedy",
                        "priority": 2
                    },
                    {
                        "title": "Gentle Movement",
                        "description": "If appropriate, gentle stretching or light activity may help with recovery. Stop if pain increases.",
                        "type": "self-care",
                        "priority": 3
                    },
                    {
                        "title": "Medical Consultation",
                        "description": "If symptoms are severe, persistent, or worsening, consult a healthcare professional for proper diagnosis and treatment.",
                        "type": "lifestyle",
                        "priority": 1
                    }
                ]
            }
        
        # Call Gemini API
        try:
            # Configure the generation model (Gemini 1.5 Flash)
            generation_config = {
                "temperature": 0.3,
                "top_p": 0.9,
                "top_k": 32,
                "max_output_tokens": 2048,
            }
            
            # Setup the safety settings
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
            ]
            
            # Initialize Gemini model (use flash for faster response)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                safety_settings=safety_settings
            )

            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract and parse the response to get valid JSON
            result_text = response.text.strip()
            
            # Extract JSON from the response which might have markdown backticks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Parse the JSON
            result = json.loads(result_text)
            return result
        except Exception as api_error:
            # Log the specific API error
            logging.error(f"Gemini API error: {str(api_error)}")
            
            # Provide a more specific error message
            if "quota" in str(api_error).lower() or "rate" in str(api_error).lower():
                raise Exception("Gemini API quota or rate limit reached. Please try again later.")
            
            # If there's an error in JSON parsing, return a structured response
            if "JSONDecodeError" in str(api_error) or "json" in str(api_error).lower():
                raise Exception("The AI model returned an invalid response format. Please try again.")
            
            # Re-raise the exception for other API errors
            raise
    
    except Exception as e:
        logging.error(f"Error generating anonymous recovery suggestions: {str(e)}")
        # Raise the exception so the route can handle it and show a user-friendly message
        raise

def generate_recovery_plan(user, journal_entries):
    """
    Generate a recovery plan using Google's Gemini 1.5 Flash model based on user's symptoms
    """
    try:
        symptoms_data = [
            {
                'symptom': entry.symptom,
                'description': entry.description,
                'severity': entry.severity,
                'date': entry.date_experienced.strftime('%Y-%m-%d')
            }
            for entry in journal_entries
        ]

        prompt = f"""
        As a medical AI assistant, generate a recovery plan for a patient with the following symptoms:

        Patient Information:
        Age: {user.age or 'Not provided'}
        Gender: {user.gender or 'Not provided'}
        Weight: {user.weight or 'Not provided'} kg
        Height: {user.height or 'Not provided'} cm

        Symptoms:
        {json.dumps(symptoms_data, indent=2)}

        Generate a comprehensive recovery plan with actionable recommendations.

        Return the response in the following JSON format:
        {{
            "title": "Recovery Plan Title",
            "description": "Overall description of the plan",
            "recommendations": [
                {{
                    "title": "Recommendation Title",
                    "description": "Detailed explanation",
                    "type": "lifestyle, medication, or therapy",
                    "priority": priority level (1-3, where 1 is highest priority)
                }}
            ]
        }}

        Provide at least 4-5 recommendations. Focus on evidence-based approaches. Do not suggest specific medications by name.
        Important: Format the response as valid JSON.
        """

        # Check if Google API key is available
        if not GOOGLE_API_KEY:
            logging.error("Google API key is not available")
            # Return a fallback response
            return {
                "title": "General Recovery Plan",
                "description": "A general recovery plan based on your symptoms. Please consult with a healthcare professional for personalized advice.",
                "recommendations": [
                    {
                        "title": "Rest and Recovery",
                        "description": "Ensure adequate rest to allow your body to heal naturally. Try to get 7-9 hours of sleep per night and take breaks during the day if needed.",
                        "type": "lifestyle",
                        "priority": 1
                    },
                    {
                        "title": "Healthy Diet and Hydration",
                        "description": "Maintain a balanced diet rich in fruits, vegetables, lean proteins, and whole grains. Stay well-hydrated by drinking plenty of water throughout the day.",
                        "type": "lifestyle",
                        "priority": 2
                    },
                    {
                        "title": "Physical Activity as Tolerated",
                        "description": "Engage in gentle physical activity as your condition allows. Start with walking or light stretching and gradually increase intensity based on your comfort level.",
                        "type": "therapy",
                        "priority": 2
                    },
                    {
                        "title": "Stress Management",
                        "description": "Practice stress reduction techniques such as deep breathing, meditation, or gentle yoga. Consider keeping a journal to track symptoms and stressors.",
                        "type": "lifestyle",
                        "priority": 3
                    },
                    {
                        "title": "Medical Follow-up",
                        "description": "Schedule a follow-up appointment with your healthcare provider to monitor your progress and adjust your treatment plan as needed.",
                        "type": "lifestyle",
                        "priority": 1
                    }
                ]
            }

        # Call Gemini API
        try:
            # Configure the generation model (Gemini 1.5 Flash)
            generation_config = {
                "temperature": 0.3,
                "top_p": 0.9,
                "top_k": 32,
                "max_output_tokens": 2048,
            }
            
            # Setup the safety settings
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
            ]
            
            # Initialize Gemini model (use flash for faster response)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                safety_settings=safety_settings
            )

            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract and parse the response to get valid JSON
            result_text = response.text.strip()
            
            # Extract JSON from the response which might have markdown backticks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Parse the JSON
            result = json.loads(result_text)
            return result
        except Exception as api_error:
            # Log the specific API error
            logging.error(f"Gemini API error in generate_recovery_plan: {str(api_error)}")
            
            # Provide a more specific error message
            if "quota" in str(api_error).lower() or "rate" in str(api_error).lower():
                logging.error("Gemini API quota or rate limit reached.")
            
            # If there's an error in JSON parsing, log it
            if "JSONDecodeError" in str(api_error) or "json" in str(api_error).lower():
                logging.error("The AI model returned an invalid response format.")
            
            # Return None to indicate failure
            return None

    except Exception as e:
        logging.error(f"Error generating recovery plan: {str(e)}")
        return None

def generate_nutrition_plan(user, journal_entries, allergies):
    """
    Generate a nutrition plan using Google's Gemini 1.5 Flash model based on user's symptoms and allergies
    """
    try:
        symptoms_data = [
            {
                'symptom': entry.symptom,
                'description': entry.description,
                'severity': entry.severity,
                'date': entry.date_experienced.strftime('%Y-%m-%d')
            }
            for entry in journal_entries
        ]

        allergies_data = [
            {
                'food_item': allergy.food_item,
                'severity': allergy.severity,
                'notes': allergy.notes
            }
            for allergy in allergies
        ]

        prompt = f"""
        As a nutrition AI assistant, generate a nutrition plan for a patient with the following symptoms and allergies:

        Patient Information:
        Age: {user.age or 'Not provided'}
        Gender: {user.gender or 'Not provided'}
        Weight: {user.weight or 'Not provided'} kg
        Height: {user.height or 'Not provided'} cm
        BMI: {user.calculate_bmi() or 'Not provided'}

        Symptoms:
        {json.dumps(symptoms_data, indent=2)}

        Food Allergies:
        {json.dumps(allergies_data, indent=2) if allergies_data else "No known food allergies"}

        Generate a comprehensive nutrition plan with dietary recommendations that can help address these symptoms.

        Return the response in the following JSON format:
        {{
            "title": "Nutrition Plan Title",
            "description": "Overall description of the nutrition plan",
            "recommendations": [
                {{
                    "title": "Recommendation Title",
                    "description": "Detailed explanation including suggested foods and nutrients",
                    "type": "nutrition",
                    "priority": priority level (1-3, where 1 is highest priority)
                }}
            ]
        }}

        Provide at least 5-6 nutrition recommendations. Focus on evidence-based approaches. Be specific about foods to include and avoid.
        Important: Format the response as valid JSON.
        """

        # Check if Google API key is available
        if not GOOGLE_API_KEY:
            logging.error("Google API key is not available for nutrition plan generation")
            # Return a fallback response
            return {
                "title": "General Nutrition Plan",
                "description": "A general nutrition plan to help with your symptoms. Please consult with a registered dietitian for personalized dietary advice.",
                "recommendations": [
                    {
                        "title": "Anti-Inflammatory Foods",
                        "description": "Include foods with anti-inflammatory properties such as fatty fish (salmon, mackerel), berries, leafy greens, nuts, olive oil, and turmeric. These can help reduce inflammation and improve overall health.",
                        "type": "nutrition",
                        "priority": 1
                    },
                    {
                        "title": "Adequate Hydration",
                        "description": "Drink 8-10 glasses of water daily. Proper hydration supports all bodily functions, helps flush toxins, aids digestion, and can reduce the severity of many symptoms.",
                        "type": "nutrition",
                        "priority": 1
                    },
                    {
                        "title": "Balanced Macronutrients",
                        "description": "Ensure each meal contains a balance of lean protein, complex carbohydrates, and healthy fats. This provides sustained energy and helps stabilize blood sugar levels.",
                        "type": "nutrition",
                        "priority": 2
                    },
                    {
                        "title": "Fiber-Rich Foods",
                        "description": "Include plenty of fiber from whole grains, vegetables, fruits, and legumes. Fiber supports digestive health, helps maintain healthy weight, and can improve many gastrointestinal symptoms.",
                        "type": "nutrition",
                        "priority": 2
                    },
                    {
                        "title": "Limit Processed Foods",
                        "description": "Reduce consumption of highly processed foods, refined sugars, and artificial additives. These can trigger inflammation and worsen many health conditions.",
                        "type": "nutrition",
                        "priority": 3
                    },
                    {
                        "title": "Food Journal",
                        "description": "Keep a food journal to track how different foods affect your symptoms. This can help identify specific trigger foods that may need to be avoided in your individual case.",
                        "type": "nutrition",
                        "priority": 3
                    }
                ]
            }
        
        # Call Gemini API
        try:
            # Configure the generation model (Gemini 1.5 Flash)
            generation_config = {
                "temperature": 0.3,
                "top_p": 0.9,
                "top_k": 32,
                "max_output_tokens": 2048,
            }
            
            # Setup the safety settings
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
            ]
            
            # Initialize Gemini model (use flash for faster response)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                safety_settings=safety_settings
            )

            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract and parse the response to get valid JSON
            result_text = response.text.strip()
            
            # Extract JSON from the response which might have markdown backticks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Parse the JSON
            result = json.loads(result_text)
            return result
        except Exception as api_error:
            # Log the specific API error
            logging.error(f"Gemini API error in generate_nutrition_plan: {str(api_error)}")
            
            # Provide a more specific error message
            if "quota" in str(api_error).lower() or "rate" in str(api_error).lower():
                logging.error("Gemini API quota or rate limit reached for nutrition plan.")
            
            # If there's an error in JSON parsing, log it
            if "JSONDecodeError" in str(api_error) or "json" in str(api_error).lower():
                logging.error("The AI model returned an invalid response format for nutrition plan.")
            
            # Return None to indicate failure
            return None

    except Exception as e:
        logging.error(f"Error generating nutrition plan: {str(e)}")
        return None

def generate_sports_recovery_plan(user, journal_entries, activities):
    """
    Generate a sports recovery plan using Google's Gemini 1.5 Flash model based on user's symptoms and athletic activities
    """
    try:
        symptoms_data = [
            {
                'symptom': entry.symptom,
                'description': entry.description,
                'severity': entry.severity,
                'date': entry.date_experienced.strftime('%Y-%m-%d')
            }
            for entry in journal_entries
        ]

        activities_data = [
            {
                'name': activity.name,
                'frequency': activity.frequency,
                'intensity': activity.intensity,
                'notes': activity.notes
            }
            for activity in activities
        ]

        prompt = f"""
        As a sports medicine AI assistant, generate a sports recovery plan for an athlete with the following symptoms and activities:

        Athlete Information:
        Age: {user.age or 'Not provided'}
        Gender: {user.gender or 'Not provided'}
        Weight: {user.weight or 'Not provided'} kg
        Height: {user.height or 'Not provided'} cm

        Athletic Activities:
        {json.dumps(activities_data, indent=2)}

        Symptoms/Injuries:
        {json.dumps(symptoms_data, indent=2)}

        Generate a comprehensive sports recovery plan with actionable recommendations specifically tailored for athletes.

        Return the response in the following JSON format:
        {{
            "title": "Sports Recovery Plan Title",
            "description": "Overall description of the plan",
            "recommendations": [
                {{
                    "title": "Recommendation Title",
                    "description": "Detailed explanation including exercises, modifications, and recovery techniques",
                    "type": "sports",
                    "priority": priority level (1-3, where 1 is highest priority)
                }}
            ]
        }}

        Provide at least 5-6 sports-specific recommendations. Focus on evidence-based approaches for athletic recovery.
        Important: Format the response as valid JSON.
        """

        # Check if Google API key is available
        if not GOOGLE_API_KEY:
            logging.error("Google API key is not available for sports recovery plan generation")
            # Return a fallback response
            return {
                "title": "General Sports Recovery Plan",
                "description": "A general sports recovery plan for your symptoms and activities. Please consult with a sports medicine professional for personalized advice.",
                "recommendations": [
                    {
                        "title": "Active Recovery",
                        "description": "Engage in low-intensity activities like walking, swimming, or cycling at 30-40% of your maximum effort. Active recovery promotes blood flow to injured areas without causing additional stress, helping your body heal faster.",
                        "type": "sports",
                        "priority": 1
                    },
                    {
                        "title": "Targeted Stretching",
                        "description": "Perform gentle stretching for 10-15 minutes daily, focusing on the affected areas and surrounding muscle groups. Hold each stretch for 30 seconds without bouncing. This helps maintain flexibility and range of motion during recovery.",
                        "type": "sports",
                        "priority": 1
                    },
                    {
                        "title": "Contrast Therapy",
                        "description": "Apply alternating cold (1-2 minutes) and heat (3-4 minutes) to affected areas for 15-20 minutes total. Cold reduces inflammation while heat increases blood flow, speeding recovery when used in combination.",
                        "type": "sports",
                        "priority": 2
                    },
                    {
                        "title": "Proper Nutrition and Hydration",
                        "description": "Increase protein intake to 1.6-2.0g/kg of body weight and ensure adequate carbohydrate consumption. Stay well-hydrated with 2-3 liters of water daily. Proper nutrition provides the building blocks needed for tissue repair.",
                        "type": "sports",
                        "priority": 2
                    },
                    {
                        "title": "Adequate Rest Periods",
                        "description": "Ensure 7-9 hours of quality sleep per night and incorporate rest days into your training schedule. Sleep is when most cellular repair occurs, making it essential for recovery.",
                        "type": "sports",
                        "priority": 1
                    },
                    {
                        "title": "Gradual Return to Activity",
                        "description": "Follow a progressive return-to-play protocol, starting at 25% of normal intensity and volume. Increase by 10-15% per week as symptoms allow. This gradual approach prevents re-injury while rebuilding strength and endurance.",
                        "type": "sports",
                        "priority": 3
                    }
                ]
            }
        
        # Call Gemini API
        try:
            # Configure the generation model (Gemini 1.5 Flash)
            generation_config = {
                "temperature": 0.3,
                "top_p": 0.9,
                "top_k": 32,
                "max_output_tokens": 2048,
            }
            
            # Setup the safety settings
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
            ]
            
            # Initialize Gemini model (use flash for faster response)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                safety_settings=safety_settings
            )

            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract and parse the response to get valid JSON
            result_text = response.text.strip()
            
            # Extract JSON from the response which might have markdown backticks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Parse the JSON
            result = json.loads(result_text)
            return result
        except Exception as api_error:
            # Log the specific API error
            logging.error(f"Gemini API error in generate_sports_recovery_plan: {str(api_error)}")
            
            # Provide a more specific error message
            if "quota" in str(api_error).lower() or "rate" in str(api_error).lower():
                logging.error("Gemini API quota or rate limit reached for sports recovery plan.")
            
            # If there's an error in JSON parsing, log it
            if "JSONDecodeError" in str(api_error) or "json" in str(api_error).lower():
                logging.error("The AI model returned an invalid response format for sports recovery plan.")
            
            # Return None to indicate failure
            return None

    except Exception as e:
        logging.error(f"Error generating sports recovery plan: {str(e)}")
        return None