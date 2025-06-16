# CS2 Music Kit Recommender

A modern web application that recommends CS2 music kits based on your current feelings and mood using AI.

## Features

- **Intelligent Recommendations**: Uses Google's Gemini AI to analyze your feelings and suggest the perfect music kit
- **Interactive UI**: Beautiful, modern interface with sliders and mood selectors
- **CS:GO Loading Messages**: Authentic loading experience with real CS:GO loading messages
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Real-time Data**: Fetches the latest music kit data from the CS:GO API

## How It Works

1. **Set Your Feelings**: Use sliders to indicate your energy level, aggressiveness, focus, and confidence
2. **Choose Your Mood**: Select from various mood options (excited, focused, chill, competitive, etc.)
3. **Get Recommendation**: The AI analyzes your input and recommends the perfect music kit
4. **Share Results**: Share your recommendation with friends

## Tech Stack

- **Backend**: Python + Flask
- **AI**: Google Gemini AI (via @google/genai)
- **Frontend**: Vanilla JavaScript, Modern CSS
- **Data Source**: [ByMykel/CSGO-API](https://github.com/ByMykel/CSGO-API)
- **Deployment**: Vercel

## Setup for Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Google AI API key:
   ```bash
   export GOOGLE_AI_API_KEY=your_api_key_here
   ```
4. Run the application:
   ```bash
   python app.py
   ```

## Environment Variables

- `GOOGLE_AI_API_KEY`: Your Google AI API key for Gemini

## Deployment to Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Login: `vercel login`
3. Deploy: `vercel`
4. Set environment variable: `vercel env add GOOGLE_AI_API_KEY`

## API Endpoints

- `GET /`: Main application page
- `POST /api/recommend`: Get music kit recommendation based on feelings
- `GET /api/loading-message`: Get random CS:GO loading message
- `GET /api/music-kits`: Get all available music kits

## Contributing

Feel free to submit issues and pull requests. This project is made for the CS2 community!

## License

This project is open source and available under the MIT License.

## Credits

- Music kit data from [ByMykel/CSGO-API](https://github.com/ByMykel/CSGO-API)
- Loading messages from CS:GO game files
- Built with ❤️ for the CS2 community
