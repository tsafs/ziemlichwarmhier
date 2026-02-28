export interface PlotRegistryEntry {
    id: string;
    loader: () => Promise<{ default: React.ComponentType<any> }>;
}

export const plots: PlotRegistryEntry[] = [
    {
        id: 'climate-map',
        loader: () => import('../maps/ClimateMap/View'),
    },
];
