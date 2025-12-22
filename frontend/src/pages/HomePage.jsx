import Header from '../components/Layout/Header';
import AvatarGenerator from '../components/Avatar/AvatarGenerator';
import './HomePage.css';

export default function HomePage() {
    return (
        <div className="home-page">
            <Header />
            <main className="main-content">
                <AvatarGenerator />
            </main>
        </div>
    );
}
