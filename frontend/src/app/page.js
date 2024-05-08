"use client";

import { useState } from 'react';
import axios from 'axios';

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
            console.log(response.data); // Logging the response to see what is received
            setResults(response.data);
        } catch (error) {
            console.error('Error fetching data:', error.response || error);
            alert('Failed to fetch data. Check console for more details.');
        }
    };

    return (
        <div>
            <input 
                type="text" 
                placeholder="Enter product name" 
                value={productName} 
                onChange={(e) => setProductName(e.target.value)}
            />
            <button onClick={handleSearch}>Search</button>
            <table>
                <thead>
                    <tr>
                        <th>Site</th>
                        <th>Item title name</th>
                        <th>Price (USD)</th>
                    </tr>
                </thead>
                <tbody>
                    {results.map((result, index) => (
                        <tr key={index}>
                            <td>{result.Site}</td>
                            <td>
                                {result['Price(USD)'] !== 'Price not found' ? (
                                    <a href={result.Link} target="_blank" rel="noopener noreferrer">
                                        {result['Item title name']}
                                    </a>
                                ) : (
                                    <span>{result['Item title name']}</span>
                                )}
                            </td>
                            <td>{result['Price(USD)']}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
