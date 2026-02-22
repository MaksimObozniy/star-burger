import "core-js/stable";
import "regenerator-runtime/runtime";

import { createRoot } from 'react-dom/client';
import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import './css/products.css';
import './css/product.css';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);

// Workaround for Parcel bug https://github.com/parcel-bundler/parcel/issues/2894
if (module.hot) {
  module.hot.accept(function () {
    setTimeout(function() {
      location.reload();
    }, 300);
  });
}
