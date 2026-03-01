import { SignUp } from '@clerk/clerk-react';
import TerminalBackground from '../components/TerminalBackground';
import './Auth.css';

export default function Register() {
  return (
    <div className="auth-container">
      <TerminalBackground />
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', zIndex: 10, position: 'relative' }}>
        <SignUp signInUrl="/login" forceRedirectUrl="/onboarding" />
      </div>
    </div>
  );
}
