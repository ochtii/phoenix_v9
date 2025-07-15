// Firebase Web Configuration für Frontend
// Diese Datei wird für die clientseitige Firebase-Initialisierung verwendet

const firebaseConfig = {
  apiKey: "AIzaSyDx54-pZxmxa3vPCMpZPSPRiH0h14XuXKE",
  authDomain: "phoenix-v9.firebaseapp.com",
  projectId: "phoenix-v9",
  storageBucket: "phoenix-v9.firebasestorage.app",
  messagingSenderId: "242144683296",
  appId: "1:242144683296:web:1044f886532c0e90f2a345",
  measurementId: "G-2KJHLM2CRF"
};

// Firebase für Frontend initialisieren (falls benötigt)
// import { initializeApp } from 'firebase/app';
// import { getAuth } from 'firebase/auth';
// import { getFirestore } from 'firebase/firestore';

// const app = initializeApp(firebaseConfig);
// export const auth = getAuth(app);
// export const db = getFirestore(app);

// Für einfache Verwendung in HTML
window.firebaseConfig = firebaseConfig;
