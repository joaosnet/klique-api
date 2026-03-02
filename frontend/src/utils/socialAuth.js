import { Capacitor } from '@capacitor/core';

/**
 * Sign in with Google on native Android via Capacitor plugin.
 * Returns the idToken string.
 */
export async function googleSignInNative() {
    const { GoogleAuth } = await import('@codetrix-studio/capacitor-google-auth');
    const result = await GoogleAuth.signIn();
    // The plugin returns { authentication: { idToken } } on Android
    const idToken = result.authentication?.idToken || result.idToken;
    if (!idToken) {
        throw new Error('Google Sign-In: no idToken received');
    }
    return idToken;
}

/**
 * Sign in with Apple using the AppleID JS SDK on web.
 * Returns { idToken, name } where name may be null.
 */
export async function appleSignInWeb() {
    // Load Apple JS SDK if not already loaded
    if (!window.AppleID) {
        await new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://appleid.cdn-apple.com/appleauth/static/jsapi/appleid/1/en_US/appleid.auth.js';
            script.onload = resolve;
            script.onerror = () => reject(new Error('Failed to load Apple JS SDK'));
            document.head.appendChild(script);
        });
    }

    const clientId = import.meta.env.VITE_APPLE_CLIENT_ID;
    const redirectURI = import.meta.env.VITE_APPLE_REDIRECT_URI || window.location.origin;

    window.AppleID.auth.init({
        clientId,
        scope: 'name email',
        redirectURI,
        usePopup: true,
    });

    const response = await window.AppleID.auth.signIn();
    const idToken = response.authorization?.id_token;
    if (!idToken) {
        throw new Error('Apple Sign-In: no id_token received');
    }

    // Apple only provides the user's name on the FIRST login
    const fullName = response.user?.name;
    let name = null;
    if (fullName) {
        name = [fullName.firstName, fullName.lastName].filter(Boolean).join(' ');
    }

    return { idToken, name };
}

/**
 * Sign in with Apple on native platforms via Capacitor plugin.
 * Returns { idToken, name }.
 */
export async function appleSignInNative() {
    const { SignInWithApple } = await import('@capacitor-community/apple-sign-in');
    const result = await SignInWithApple.authorize({
        clientId: import.meta.env.VITE_APPLE_CLIENT_ID,
        redirectURI: import.meta.env.VITE_APPLE_REDIRECT_URI || window.location.origin,
        scopes: 'name email',
    });

    const idToken = result.response?.identityToken;
    if (!idToken) {
        throw new Error('Apple Sign-In: no identityToken received');
    }

    const name = [result.response?.givenName, result.response?.familyName]
        .filter(Boolean)
        .join(' ') || null;

    return { idToken, name };
}

/**
 * Check if we're running on a native platform (Android/iOS).
 */
export function isNativePlatform() {
    return Capacitor.isNativePlatform();
}
