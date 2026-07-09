import { createContext, useContext, useReducer, useCallback } from "react";

const WorkspaceContext = createContext(null);

const initialState = {
  selectedCollectionId: null,
  collectionName: null,
  selectedDocumentIds: [],
  documents: [],
  activeDocumentId: null,
  activeChunkId: null,
  generatedProducts: [],
  sourcesCollapsed: true,
  studioCollapsed: true,
  activeTrace: null,
};

function reducer(state, action) {
  switch (action.type) {
    case "SELECT_COLLECTION":
      return {
        ...state,
        selectedCollectionId: action.collectionId,
        collectionName: action.collectionName,
        documents: action.documents,
        selectedDocumentIds: action.documents.map((d) => d.id),
        activeDocumentId: null,
        activeChunkId: null,
        activeTrace: null,
      };
    case "TOGGLE_DOCUMENT": {
      const ids = state.selectedDocumentIds.includes(action.documentId)
        ? state.selectedDocumentIds.filter((id) => id !== action.documentId)
        : [...state.selectedDocumentIds, action.documentId];
      return { ...state, selectedDocumentIds: ids };
    }
    case "SET_DOCUMENTS":
      return { ...state, documents: action.documents };
    case "SET_ACTIVE_DOCUMENT":
      return {
        ...state,
        activeDocumentId: action.documentId,
        activeChunkId: action.documentId === null ? null : state.activeChunkId,
      };
    case "SET_ACTIVE_CHUNK":
      return {
        ...state,
        activeChunkId: action.chunkId,
        activeDocumentId: action.documentId !== undefined ? action.documentId : state.activeDocumentId,
        sourcesCollapsed: action.chunkId ? false : state.sourcesCollapsed,
      };
    case "ADD_GENERATED_PRODUCT":
      return {
        ...state,
        generatedProducts: [action.product, ...state.generatedProducts],
      };
    case "TOGGLE_SOURCES_PANEL": {
      const nextCollapsed = !state.sourcesCollapsed;
      return {
        ...state,
        sourcesCollapsed: nextCollapsed,
        activeChunkId: nextCollapsed ? null : state.activeChunkId,
      };
    }
    case "TOGGLE_STUDIO_PANEL":
      return { ...state, studioCollapsed: !state.studioCollapsed };
    case "SET_ACTIVE_TRACE":
      return { ...state, activeTrace: action.trace };
    default:
      return state;
  }
}

export function WorkspaceProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const selectCollection = useCallback(
    (collectionId, collectionName, documents) =>
      dispatch({ type: "SELECT_COLLECTION", collectionId, collectionName, documents }),
    []
  );

  const toggleDocument = useCallback(
    (documentId) => dispatch({ type: "TOGGLE_DOCUMENT", documentId }),
    []
  );

  const setDocuments = useCallback(
    (documents) => dispatch({ type: "SET_DOCUMENTS", documents }),
    []
  );

  const setActiveDocument = useCallback(
    (documentId) => dispatch({ type: "SET_ACTIVE_DOCUMENT", documentId }),
    []
  );

  const setActiveChunkId = useCallback(
    (chunkId, documentId) => dispatch({ type: "SET_ACTIVE_CHUNK", chunkId, documentId }),
    []
  );

  const addGeneratedProduct = useCallback(
    (product) => dispatch({ type: "ADD_GENERATED_PRODUCT", product }),
    []
  );

  const toggleSourcesPanel = useCallback(
    () => dispatch({ type: "TOGGLE_SOURCES_PANEL" }),
    []
  );

  const toggleStudioPanel = useCallback(
    () => dispatch({ type: "TOGGLE_STUDIO_PANEL" }),
    []
  );

  const setActiveTrace = useCallback(
    (trace) => dispatch({ type: "SET_ACTIVE_TRACE", trace }),
    []
  );

  return (
    <WorkspaceContext.Provider
      value={{
        ...state,
        selectCollection,
        toggleDocument,
        setDocuments,
        setActiveDocument,
        setActiveChunkId,
        addGeneratedProduct,
        toggleSourcesPanel,
        toggleStudioPanel,
        setActiveTrace,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) throw new Error("useWorkspace must be used within WorkspaceProvider");
  return ctx;
}
