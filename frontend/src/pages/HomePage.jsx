import Header from '../components/Layout/Header';
import AvatarGenerator from '../components/Avatar/AvatarGenerator';
import OnboardingTutorial, { useOnboarding } from '../components/Onboarding/OnboardingTutorial';
import './HomePage.css';

export default function HomePage() {
    const { showOnboarding, completeOnboarding } = useOnboarding();

    return (
        <div className="home-page">
            <Header />
            <main className="main-content">
                <AvatarGenerator />
            </main>

            {/* Tutorial para usuários novos */}
            {showOnboarding && (
                <OnboardingTutorial onComplete={completeOnboarding} />
            )}
        </div>
    );
}
