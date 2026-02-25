# Opportunity Access Platform - Web Application

React web application built with Vite for discovering and tracking educational and professional opportunities.

## Features

- User authentication (register/login)
- Personalized opportunity recommendations
- Search and filter opportunities
- Save opportunities to tracker
- Track application deadlines
- User profile management
- Responsive design for desktop and mobile browsers

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Backend API running at `http://localhost:8000`

## Installation

1. Install dependencies:
```bash
cd web
npm install
```

## Running the App

1. Make sure the backend API is running at `http://localhost:8000`

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:3000`

## Building for Production

1. Build the application:
```bash
npm run build
```

2. Preview the production build:
```bash
npm run preview
```

The built files will be in the `dist` directory, ready to be deployed to any static hosting service.

## Project Structure

```
web/
├── index.html                  # HTML entry point
├── vite.config.js             # Vite configuration
├── package.json               # Dependencies
├── src/
│   ├── main.jsx              # React entry point
│   ├── App.jsx               # Main app component with routing
│   ├── index.css             # Global styles
│   ├── components/
│   │   ├── Layout.jsx        # Main layout with navigation
│   │   ├── Layout.css
│   │   ├── OpportunityCard.jsx  # Reusable opportunity card
│   │   └── OpportunityCard.css
│   ├── pages/
│   │   ├── Login.jsx         # Login page
│   │   ├── Register.jsx      # Registration page
│   │   ├── Home.jsx          # Home with recommendations
│   │   ├── Opportunities.jsx # Search opportunities
│   │   ├── OpportunityDetail.jsx # Opportunity details
│   │   ├── Tracked.jsx       # Saved opportunities
│   │   ├── Profile.jsx       # User profile
│   │   ├── Auth.css          # Auth pages styles
│   │   └── Pages.css         # Pages styles
│   └── services/
│       └── api.js            # API client
```

## API Configuration

The app uses Vite's proxy feature to connect to the backend API. The proxy is configured in `vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

For production, you'll need to configure your web server to proxy API requests or update the API base URL in `src/services/api.js`.

## Deployment

### Static Hosting (Netlify, Vercel, etc.)

1. Build the app:
```bash
npm run build
```

2. Deploy the `dist` directory to your hosting service

3. Configure redirects for client-side routing:
   - For Netlify: Create `public/_redirects` with `/* /index.html 200`
   - For Vercel: Create `vercel.json` with appropriate rewrites

### Docker

Create a `Dockerfile`:
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Environment Variables

For production, you may want to use environment variables:

Create `.env.production`:
```
VITE_API_URL=https://your-api-domain.com/api
```

Update `src/services/api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Cannot connect to API
- Ensure the backend is running at `http://localhost:8000`
- Check browser console for CORS errors
- Verify proxy configuration in `vite.config.js`

### Build errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`
- Update dependencies: `npm update`

### Routing issues in production
- Ensure your web server is configured for client-side routing
- All routes should serve `index.html`

## License

MIT
