"use client";
import { useState } from 'react';
import axios from 'axios';
import styles from './page.module.css';

export default function Home() {
  const [productName, setProductName] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    if (!productName.trim()) {
      alert('Please enter a product name');
      return;
    }

    try {
      const response = await axios.get(`http://localhost:8000/search/${encodeURIComponent(productName)}`);
      setResults(response.data);
    } catch (error) {
      console.error('Error fetching data:', error.response || error);
      alert('Failed to fetch data. Check console for more details.');
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.explanation}>Find Product</h1>
      <div className={styles.searchForm}>
        <input
          type="text"
          placeholder="Search for products"
          value={productName}
          onChange={(e) => setProductName(e.target.value)}
          className={styles.searchInput}
        />
        <button onClick={handleSearch} className={styles.searchButton}>
          Search
        </button>
      </div>

      <div className={styles.results}>
        <table className={styles.resultsTable}>
          <thead>
            <tr>
              <th className={styles.tableHeader}>Site</th>
              <th className={styles.tableHeader}>Item Title Name</th>
              <th className={styles.tableHeader}>Price (USD)</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result, index) => (
              <tr key={index} className={styles.tableRow}>
                <td className={styles.tableCell}>{result.Site}</td>
                <td className={styles.tableCell}>
                  {result['Price(USD)'] !== 'Price not found' ? (
                    <a href={result.Link} target="_blank" rel="noopener noreferrer" className={styles.productLink}>
                      {result['Item title name']}
                    </a>
                  ) : (
                    <span>{result['Item title name']}</span>
                  )}
                </td>
                <td className={styles.tableCell}>{result['Price(USD)']}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
