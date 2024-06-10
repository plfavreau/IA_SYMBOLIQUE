'use client';

import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ArrowUp, Loader2 } from 'lucide-react';
import { Inter } from 'next/font/google';
import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const inter = Inter({ subsets: ['latin'] });

function useAutoGrowTextArea(initialValue: string) {
  const [value, setValue] = useState(initialValue);
  const textAreaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    if (textAreaRef.current) {
      textAreaRef.current.style.height = 'auto';
      textAreaRef.current.style.height = `${textAreaRef.current.scrollHeight}px`;
    }
  }, [value]);

  const handleChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(event.target.value);
  };

  return {
    value,
    onChange: handleChange,
    ref: textAreaRef,
    setValue,
  };
}

const planningExamples = [
  {
    emoji: '📚',
    description:
      'In my school there are rooms 201, 202, 203. I have 3 lessons: Math, Physics, Chemistry. I have 3 timeslots: Monday 8:30-9:30, Monday 9:30-10:30, Monday 10:30-11:30.',
  },
  {
    emoji: '⏰',
    description:
      'I have 4 hours math lesson, 3 hours physics lesson, 2 hours chemistry lesson. I have 3 rooms: Room A, Room B, Room C. Lessons can be planned anytime in the week from monday to friday, from 8:30 to 15:30.',
  },
  {
    emoji: '🎓',
    description:
      "J'ai 8 heures de cours de IA-Symbolique à planifier avec Jean-Sylvain Boige entre le lundi et le mercredi (8h-19h30).",
  },
  {
    emoji: '🍎',
    description: 'Tu peux me donner la recette de la tarte aux pommes ?',
  },
];

type LLMError = {
  error: string;
};

type LLMResponseOK = {
  room_markdown: string,
  teacher_markdown: string,
  student_group_markdown: string,
}

type LLMResponse = LLMError & LLMResponseOK;

export default function Home() {
  const textareaProps = useAutoGrowTextArea('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState('');

  const handleSend = async () => {
    setLoading(true);
    setResponse('');

    const llmResponse = await fetch('http://127.0.0.1:8000', {
      method: 'POST',
      body: JSON.stringify({ text: textareaProps.value }),
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const llmResponseJson: LLMResponse = await llmResponse.json();
    console.log(JSON.stringify(llmResponseJson));
    if (llmResponseJson.error) {
      setResponse("Planning solver failed : " + llmResponseJson.error);
      setLoading(false);
      return;
    }
    setResponse(`Per room : \n${llmResponseJson.room_markdown} \n\nPer teacher : \n${llmResponseJson.teacher_markdown} \n\nPer student group : \n${llmResponseJson.student_group_markdown}`);
    setLoading(false);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && event.ctrlKey && textareaProps.value) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <main className='flex flex-col items-center justify-between p-24'>
      <div className='flex flex-col h-full w-full'>
        <div className='mb-32 flex flex-col items-center space-y-4'>
          <motion.h2
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.2 }}
            className='mb-3 text-3xl font-light text-gray-900'
          >
            LLM Planner
          </motion.h2>
          <div className='flex flex-row justify-evenly py-8'>
            {planningExamples.map((example, index) => (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  duration: 0.3,
                  delay: 0.2 + index / 10,
                  type: 'just',
                }}
                key={index}
                onClick={() => {
                  textareaProps.setValue(example.description);
                  console.log('clicked');
                }}
                className='flex flex-col space-y-2 border border-gray-300/60 hover:bg-slate-50/80 rounded-xl p-4 w-1/5 shadow-sm'
              >
                <div className='flex items-center justify-center'>
                  <div className='text-2xl'>{example.emoji}</div>
                </div>
                <div className='flex'>
                  <button draggable className='text-sm text-gray-600'>
                    {example.description}
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
          <AnimatePresence>
            {response && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                className='text-gray-800 mt-2'
              >
                <Textarea className='w-[1024px] h-[512px] resize-none'>
                  {response}
                </Textarea>
              </motion.div>
            )}
          </AnimatePresence>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className='flex w-[45%] justify-center items-center p-4 rounded-lg'
          >
            <div className='flex w-3/4 items-center'>
              <Textarea
                onKeyDown={handleKeyDown}
                ref={textareaProps.ref}
                value={textareaProps.value}
                className='overflow-hidden resize-none rounded-2xl bg-gray-50 text-gray-500 shadow-sm'
                placeholder='Type planning problem here !'
                onChange={textareaProps.onChange}
              />
            </div>
            <Button
              disabled={!textareaProps.value || loading}
              title='CTRL + Enter to send'
              variant={'default'}
              onClick={handleSend}
              className='h-12 w-12 ml-4 flex items-center rounded-2xl justify-center shadow-sm'
            >
              {loading ? (
                <Loader2 className='animate-spin' size={24} color='white' />
              ) : (
                <ArrowUp size={24} color='white' />
              )}
            </Button>
          </motion.div>
        </div>
      </div>
    </main>
  );
}
