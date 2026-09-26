import React from 'react';
import { Card } from '../base_ui';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell,
  RadarChart, Radar, PolarAngleAxis, PolarRadiusAxis,
  ScatterChart, Scatter
} from 'recharts';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#0088fe'];

export interface KPIData {
  name: string;
  uv: number;
  pv: number;
  visit: number;
}

export const BarChartComponent: React.FC<{data: KPIData[]}> = ({data}) => (
  <Card elevated={true}>
    <h3>Bar Chart - PV/UV Comparison</h3>
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <XAxis dataKey="name" />
        <YAxis label="" />
        <Tooltip />
        <Legend />
        <Bar dataKey="pv" name="PV" fill={COLORS[0]} />
        <Bar dataKey="uv" name="UV" fill={COLORS[1]} />
      </BarChart>
    </ResponsiveContainer>
  </Card>
);

export const LineChartComponent: React.FC<{data: KPIData[]}> = ({data}) => (
  <Card elevated={true}>
    <h3>Line Chart - Trend Over Time</h3>
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis dataKey="name" />
        <YAxis label="" />
        <Tooltip />
        <Legend />
        <Line dataKey="pv" name="PV" stroke={COLORS[0]} dot={false} />
        <Line dataKey="uv" name="UV" stroke={COLORS[1]} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  </Card>
);

export const AreaChartComponent: React.FC<{data: KPIData[]}> = ({data}) => (
  <Card elevated={true}>
    <h3>Area Chart - Cumulative View</h3>
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <XAxis dataKey="name" />
        <YAxis label="" />
        <Tooltip />
        <Legend />
        <Area dataKey="pv" name="PV" stroke={COLORS[0]} fill={COLORS[0]} fillOpacity={0.3} />
        <Area dataKey="uv" name="UV" stroke={COLORS[1]} fill={COLORS[1]} fillOpacity={0.3} />
      </AreaChart>
    </ResponsiveContainer>
  </Card>
);

export const PieChartComponent: React.FC<{data: KPIData[]}> = ({data}) => (
  <Card elevated={true}>
    <h3>Pie Chart - Distribution</h3>
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          fill="#8884d8"
          dataKey="pv"
          nameKey="name"
          label={({name, percent}) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
        >
          {data.map((_, i) => <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />)}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  </Card>
);

export const RadarChartComponent: React.FC<{data: KPIData[]}> = ({data}) => (
  <Card elevated={true}>
    <h3>Radar Chart - Multi-dimensional</h3>
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data} cx={300} cy={150} innerRadius={0} outerRadius={120}>
        <PolarAngleAxis dataKey="name" />
        <PolarRadiusAxis angle={30} domain={[0, 5000]} />
        <Radar name="PV" dataKey="pv" stroke={COLORS[0]} fill={COLORS[0]} fillOpacity={0.3} />
        <Radar name="UV" dataKey="uv" stroke={COLORS[1]} fill={COLORS[1]} fillOpacity={0.3} />
        <Tooltip />
        <Legend />
      </RadarChart>
    </ResponsiveContainer>
  </Card>
);

export const ScatterChartComponent: React.FC<{data: KPIData[]}> = ({data}) => (
  <Card elevated={true}>
    <h3>Scatter Chart - Correlation</h3>
    <ResponsiveContainer width="100%" height={300}>
      <ScatterChart>
        <XAxis dataKey="pv" name="PV" domain={[0, 5000]} />
        <YAxis dataKey="uv" name="UV" domain={[0, 500]} />
        <Tooltip />
        <Legend />
        <Scatter name="PV vs UV" data={data} fill={COLORS[2]} shape="circle" />
      </ScatterChart>
    </ResponsiveContainer>
  </Card>
);

export const DashboardComponent: React.FC = () => {
  const sampleData: KPIData[] = [
    { name: 'Saadet', uv: 400, pv: 2400, visit: 3800 },
    { name: 'İhsan', uv: 300, pv: 1398, visit: 2210 },
    { name: 'Utku', uv: 200, pv: 980, visit: 1200 },
    { name: 'Meme', uv: 278, pv: 3908, visit: 4800 },
    { name: 'Hakan', uv: 180, pv: 1908, visit: 3900 },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '24px', padding: '24px' }}>
      <BarChartComponent data={sampleData} />
      <LineChartComponent data={sampleData} />
      <AreaChartComponent data={sampleData} />
      <PieChartComponent data={sampleData} />
      <RadarChartComponent data={sampleData} />
      <ScatterChartComponent data={sampleData} />
    </div>
  );
};