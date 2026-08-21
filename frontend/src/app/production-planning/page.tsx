"use client";

import React, { useState, useEffect } from 'react';
import StageWiseStockCard, { StageData } from './StageWiseStockCard';

interface ProductData {
  id: number;
  name: string;
  stock: number;
  steadyRunner: boolean;
  wipTotal: number;
  stages: StageData[];
}

export default function ProductionPlanningPage() {
  const [hideZeroStock, setHideZeroStock] = useState(false);
  const [expandedRow, setExpandedRow] = useState<number | null>(1); // default expand first row for demo
  const [products, setProducts] = useState<ProductData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // In a real application, we would fetch the list of products that need production.
    // For this demo, we'll fetch the WIP dashboard data for a single mocked product 
    // from our new FastAPI endpoint and map it to our UI state.
    
    const fetchDashboardData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/production/wip-dashboard');
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        const result = await response.json();
        
        // Mocking the overall product wrapper since our API currently returns raw stage data
        const mockProduct: ProductData = {
          id: 1,
          name: "1 UDR 11/O ULTIMATE",
          stock: 420,
          steadyRunner: true,
          wipTotal: 59.26,
          stages: [
            {
              name: "Production Forming",
              qty: 31.65,
              serials: [
                { serialNo: "ZP0095", qty: 2.35 },
                { serialNo: "ZP0136", qty: 16 },
                { serialNo: "ZP0172", qty: 13.3 },
              ]
            },
            {
              name: "Forming",
              qty: 4.52,
              serials: [
                { serialNo: "ZP0201", qty: 0.67 },
                { serialNo: "ZP0221", qty: 0.72 },
                { serialNo: "ZP0310", qty: 0.4 },
                { serialNo: "ZP0348", qty: 0.69 },
                { serialNo: "ZP0985", qty: 0.5 },
                { serialNo: "ZQ0013", qty: 1.54 },
              ]
            },
            {
              name: "Production Heat Treatment",
              qty: 2,
              serials: [
                { serialNo: "ZP0461", batchNo: "—", qty: 2 }
              ]
            },
            {
              name: "Production Weight Reduction",
              qty: 12.69,
              serials: [
                { serialNo: "ZP0901", batchNo: "BN01388", qty: 1.7 },
                { serialNo: "ZQ0095", batchNo: "BN01388", qty: 10.99 },
              ]
            }
          ]
        };

        // If the API returned real mapped stage data, we would integrate it here.
        // For now, the mock closely mirrors the requested screenshot.
        
        // Add a second product for list demonstration
        const mockProduct2: ProductData = {
            id: 2,
            name: "2 UDR 10/O STANDARD",
            stock: 120,
            steadyRunner: false,
            wipTotal: 15.00,
            stages: []
        };

        setProducts([mockProduct, mockProduct2]);
      } catch (err: any) {
        setError(err.message || 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const toggleExpand = (id: number) => {
    setExpandedRow(expandedRow === id ? null : id);
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center bg-gray-50 text-gray-500">Loading dashboard...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans p-4 max-w-5xl mx-auto">
      {/* Header section */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 bg-white rounded-md border border-gray-200 p-2 max-w-md shadow-sm">
          <span className="text-gray-700 text-sm font-medium px-2">Needs production (Planning &gt; 0)</span>
          <svg className="w-4 h-4 text-gray-400 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
        </div>
      </div>

      {/* Controls */}
      <div className="flex justify-between items-center mb-6">
        <label className="flex items-center space-x-2 cursor-pointer group">
          <input 
            type="checkbox" 
            className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            checked={hideZeroStock}
            onChange={(e) => setHideZeroStock(e.target.checked)}
          />
          <span className="text-sm text-gray-600 group-hover:text-gray-800 transition-colors">Hide zero-stock &amp; zero-sales</span>
        </label>
        <div className="text-sm text-gray-400">
          747 of 4,001 products
        </div>
      </div>

      {/* Main List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {/* Table Header */}
        <div className="grid grid-cols-12 gap-4 px-4 py-3 bg-gray-50 border-b border-gray-100 text-xs font-bold text-gray-500 uppercase tracking-wider">
          <div className="col-span-8">Product Name</div>
          <div className="col-span-4 text-right">Stock</div>
        </div>

        {/* Product Rows */}
        <div className="divide-y divide-gray-100">
          {products.map((product) => (
            <div key={product.id} className="flex flex-col">
              {/* Row Header (Clickable) */}
              <div 
                className="grid grid-cols-12 gap-4 px-4 py-4 cursor-pointer hover:bg-blue-50/50 transition-colors items-center"
                onClick={() => toggleExpand(product.id)}
              >
                <div className="col-span-8 flex items-center space-x-3">
                  <h3 className="font-bold text-slate-800">{product.name}</h3>
                  {product.steadyRunner && (
                    <span className="bg-green-100 text-green-700 text-[10px] font-bold px-2 py-0.5 rounded-sm uppercase tracking-wider">
                      Every Month
                    </span>
                  )}
                </div>
                <div className="col-span-4 text-right font-medium text-slate-700">
                  {product.stock}
                </div>
              </div>

              {/* Expanded Details */}
              {expandedRow === product.id && (
                <div className="px-4 pb-6 pt-2 bg-gray-50/50 border-t border-dashed border-gray-200 animate-in fade-in slide-in-from-top-2 duration-200">
                  
                  {/* WIP Summary row */}
                  <div className="mb-4">
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
                      Stage-wise Stock — WIP Total <span className="text-gray-800">{product.wipTotal.toFixed(2)}</span>
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {product.stages.map((stage, idx) => (
                        <div key={idx} className="bg-white border border-gray-200 rounded px-3 py-1.5 text-sm flex items-center space-x-2">
                          <span className="text-gray-600">{stage.name}:</span>
                          <span className="font-bold text-gray-900">{stage.qty.toFixed(2)}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Stage Cards Grid */}
                  <div>
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
                      Serial-wise Stock by Stage
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {product.stages.map((stage, idx) => (
                        <StageWiseStockCard key={idx} stage={stage} />
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Footer Info */}
      <div className="mt-8 text-sm text-gray-500 leading-relaxed bg-blue-50/50 p-4 rounded-lg border border-blue-100">
        In the &quot;Needs production&quot; view, products invoiced in <strong>every month</strong> of the data 
        (marked <span className="bg-green-100 text-green-700 text-[10px] font-bold px-1.5 py-0.5 rounded-sm uppercase">every month</span>) 
        are listed first as steady runners, then the rest by planning quantity. Click any product name to expand its 
        stage-wise stock and pending-order detail; expanded rows stay open until you load a new Excel file. Click 
        column headers to sort.
      </div>
    </div>
  );
}
