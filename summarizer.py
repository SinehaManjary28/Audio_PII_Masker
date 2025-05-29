from transformers import pipeline

# Load pipeline once (on first run)
topic_pipeline = pipeline("text2text-generation", model="google/flan-t5-base", max_length=50)

def classify_transcript_topic(transcript: str) -> str:
    """
    Generates a specific one-line description of what the transcript is about.
    """
    prompt = f"What is this text is about in one short sentence? {transcript}"
    result = topic_pipeline(prompt)
    return result[0]['generated_text'].strip().capitalize()
