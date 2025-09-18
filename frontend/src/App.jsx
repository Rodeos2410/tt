import React, { useState, useEffect } from 'react';
import Register from './Register';
import Login from './Login';
import Products from './Products';
import AddProduct from './AddProduct';
import Navbar from './components/Navbar';
import ProductCard from './components/ProductCard';
import ProductDetails from './ProductDetails';

function App() {
  const [userId, setUserId] = useState(() => localStorage.getItem('userId'));
  const [showRegister, setShowRegister] = useState(false);
  const [products, setProducts] = useState([]);
  const [viewProductId, setViewProductId] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/products')
      .then(res => res.json())
      .then(setProducts)
      .catch(() => setProducts([]));
  }, []);

  const handleLogin = (id) => {
    setUserId(id);
    localStorage.setItem('userId', id);
  };

  const handleLogout = () => {
    setUserId(null);
    localStorage.removeItem('userId');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar user={userId} onLogout={handleLogout} onShowRegister={setShowRegister} />
      <main className="max-w-6xl mx-auto px-4 py-6">
        {!userId ? (
          showRegister ? (
            <Register onRegister={() => setShowRegister(false)} />
          ) : (
            <Login onLogin={handleLogin} />
          )
        ) : (
          <div>
            <AddProduct ownerId={userId} onAdd={() => {}} />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              {products.map(p => (
                <ProductCard key={p.id} product={p} onView={setViewProductId} />
              ))}
            </div>
          </div>
        )}

        {viewProductId && (
          <ProductDetails id={viewProductId} onClose={() => setViewProductId(null)} userId={userId} />
        )}
      </main>
    </div>
  );
}

export default App;
