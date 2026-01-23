import { useState, KeyboardEvent } from 'react';
import { X } from 'lucide-react';
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface TagInputProps {
  placeholder?: string;
  tags: string[];
  onTagsChange: (tags: string[]) => void;
  label?: string;
}

export function TagInput({ placeholder, tags, onTagsChange, label }: TagInputProps) {
  const [inputValue, setInputValue] = useState("");

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addTag();
    } else if (e.key === 'Backspace' && inputValue === '' && tags.length > 0) {
      removeTag(tags.length - 1);
    }
  };

  const addTag = () => {
    const trimmed = inputValue.trim();
    if (trimmed && !tags.includes(trimmed)) {
      onTagsChange([...tags, trimmed]);
      setInputValue("");
    }
  };

  const removeTag = (index: number) => {
    onTagsChange(tags.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-3">
      {label && <label className="text-sm font-medium text-foreground">{label}</label>}
      <div className="flex flex-wrap gap-2 min-h-[2.5rem] p-2 rounded-xl border border-input bg-background focus-within:ring-2 focus-within:ring-ring focus-within:border-primary transition-all duration-200">
        {tags.map((tag, index) => (
          <Badge 
            key={index} 
            variant="secondary"
            className="pl-3 pr-1 py-1 text-sm bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
          >
            {tag}
            <Button
              variant="ghost"
              size="icon"
              className="h-4 w-4 ml-1 hover:bg-transparent hover:text-destructive rounded-full"
              onClick={() => removeTag(index)}
            >
              <X className="h-3 w-3" />
            </Button>
          </Badge>
        ))}
        <input
          className="flex-1 bg-transparent border-none outline-none text-sm min-w-[120px] placeholder:text-muted-foreground"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={tags.length === 0 ? placeholder : ""}
          onBlur={addTag}
        />
      </div>
      <p className="text-xs text-muted-foreground">Press Enter or comma to add</p>
    </div>
  );
}
