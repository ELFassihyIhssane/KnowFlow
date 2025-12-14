declare module "react-cytoscapejs" {
  import * as React from "react";
  import type cytoscape from "cytoscape";

  export type CytoscapeComponentProps = {
    elements?: cytoscape.ElementDefinition[] | cytoscape.ElementsDefinition;
    style?: React.CSSProperties;
    stylesheet?: cytoscape.Stylesheet[];
    layout?: cytoscape.LayoutOptions;
    cy?: (cy: cytoscape.Core) => void;
    zoom?: number;
    minZoom?: number;
    maxZoom?: number;
    pan?: cytoscape.Position;
    boxSelectionEnabled?: boolean;
    autoungrabify?: boolean;
    userZoomingEnabled?: boolean;
    userPanningEnabled?: boolean;
    className?: string;
  };

  export default class CytoscapeComponent extends React.Component<CytoscapeComponentProps> {}
}
