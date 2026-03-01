import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react';
import Login from './pages/Login';
import Register from './pages/Register';
import HomeScrollStory from './pages/HomeScrollStory';
import TrackEvent from './pages/TrackEvent';
import Opportunities from './pages/Opportunities';
import OpportunityDetail from './pages/OpportunityDetail';
import Tracked from './pages/Tracked';
import Discover from './pages/Discover';
import Profile from './pages/Profile';
import Onboarding from './pages/Onboarding';
import Layout from './components/Layout';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Scroll Story Homepage - No Layout */}
        <Route path="/" element={<HomeScrollStory />} />
        <Route path="/track" element={<TrackEvent />} />

        {/* Public routes - no auth required */}
        <Route path="/" element={<Layout />}>
          <Route path="discover" element={<Discover />} />
          <Route path="opportunities" element={<Opportunities />} />
          <Route path="opportunities/:id" element={<OpportunityDetail />} />
        </Route>

        {/* Auth routes (Handled seamlessly by Clerk) */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes - auth required */}
        <Route path="/" element={<Layout />}>
          <Route path="onboarding" element={
            <>
              <SignedIn>
                <Onboarding />
              </SignedIn>
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            </>
          } />
          <Route path="tracked" element={
            <>
              <SignedIn>
                <Tracked />
              </SignedIn>
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            </>
          } />
          <Route path="profile" element={
            <>
              <SignedIn>
                <Profile />
              </SignedIn>
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            </>
          } />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
