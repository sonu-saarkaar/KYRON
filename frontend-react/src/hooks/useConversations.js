import { useState, useEffect } from 'react';
import { chatAPI } from '../services/api';

export function useConversations() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load conversations from localStorage
  useEffect(() => {
    const loadConversations = () => {
      try {
        const stored = localStorage.getItem('kyron-conversations');
        if (stored) {
          const parsed = JSON.parse(stored);
          setConversations(parsed);
          // Set first conversation as active if none selected
          if (parsed.length > 0 && !activeConversationId) {
            setActiveConversationId(parsed[0].id);
          }
        } else {
          // Create first conversation
          const firstConv = createNewConversation();
          setConversations([firstConv]);
          setActiveConversationId(firstConv.id);
        }
      } catch (error) {
        console.error('Error loading conversations:', error);
        const firstConv = createNewConversation();
        setConversations([firstConv]);
        setActiveConversationId(firstConv.id);
      } finally {
        setLoading(false);
      }
    };

    loadConversations();
  }, []);

  // Save conversations to localStorage
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('kyron-conversations', JSON.stringify(conversations));
    }
  }, [conversations]);

  const createNewConversation = () => {
    return {
      id: `conv-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      title: 'New Conversation',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      lastMessage: null,
    };
  };

  const addConversation = () => {
    const newConv = createNewConversation();
    setConversations(prev => [newConv, ...prev]);
    setActiveConversationId(newConv.id);
    return newConv;
  };

  const deleteConversation = (id) => {
    setConversations(prev => {
      const filtered = prev.filter(c => c.id !== id);
      if (filtered.length === 0) {
        const newConv = createNewConversation();
        setActiveConversationId(newConv.id);
        return [newConv];
      }
      if (activeConversationId === id) {
        setActiveConversationId(filtered[0].id);
      }
      return filtered;
    });
  };

  const updateConversation = (id, updates) => {
    setConversations(prev => prev.map(conv => {
      if (conv.id === id) {
        return {
          ...conv,
          ...updates,
          updatedAt: new Date().toISOString(),
        };
      }
      return conv;
    }));
  };

  const addMessageToConversation = (id, message) => {
    setConversations(prev => prev.map(conv => {
      if (conv.id === id) {
        const updatedMessages = [...conv.messages, message];
        const safeText = typeof message?.text === 'string' ? message.text : '';
        // Update title from first user message if still default
        let title = conv.title;
        if (conv.title === 'New Conversation' && message.type === 'user') {
          title = safeText.substring(0, 50) || 'New Conversation';
        }
        return {
          ...conv,
          messages: updatedMessages,
          title,
          lastMessage: safeText.substring(0, 50),
          updatedAt: new Date().toISOString(),
        };
      }
      return conv;
    }));
  };

  const getActiveConversation = () => {
    return conversations.find(c => c.id === activeConversationId);
  };

  return {
    conversations,
    activeConversationId,
    setActiveConversationId,
    addConversation,
    deleteConversation,
    updateConversation,
    addMessageToConversation,
    getActiveConversation,
    loading,
  };
}

