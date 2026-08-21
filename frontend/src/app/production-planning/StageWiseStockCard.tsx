import React from 'react';

export interface SerialStock {
  serialNo: string;
  qty: number;
  batchNo?: string;
}

export interface StageData {
  name: string;
  qty: number;
  serials: SerialStock[];
}

interface StageWiseStockCardProps {
  stage: StageData;
}

export default function StageWiseStockCard({ stage }: StageWiseStockCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden min-w-[250px] flex-1">
      <div className="bg-slate-50 px-3 py-2 flex justify-between items-center border-b border-gray-100">
        <h4 className="font-semibold text-slate-800 text-sm">{stage.name}</h4>
        <span className="bg-slate-800 text-white text-xs font-bold px-2 py-0.5 rounded-full">
          {stage.qty.toFixed(2)}
        </span>
      </div>
      
      <div className="p-0">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b border-gray-100">
            <tr>
              <th scope="col" className="px-3 py-2 font-semibold tracking-wider">Serial No</th>
              {stage.serials.some(s => s.batchNo) && (
                <th scope="col" className="px-3 py-2 font-semibold tracking-wider">Batch No</th>
              )}
              <th scope="col" className="px-3 py-2 font-semibold tracking-wider text-right">Qty</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {stage.serials.length > 0 ? (
              stage.serials.map((serial, idx) => (
                <tr key={idx} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-3 py-2 font-medium text-gray-700">{serial.serialNo}</td>
                  {stage.serials.some(s => s.batchNo) && (
                    <td className="px-3 py-2 text-gray-500">{serial.batchNo || '—'}</td>
                  )}
                  <td className="px-3 py-2 text-right font-medium text-gray-900">
                    {serial.qty.toFixed(2)}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={3} className="px-3 py-4 text-center text-gray-400 italic text-xs">
                  No active serials
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
