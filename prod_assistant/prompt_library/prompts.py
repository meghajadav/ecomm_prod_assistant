from enum import Enum
from typing import Dict
import string
'''
Enum is used to create enumeration types — named constants with distinct values 
(useful to avoid magic strings and to provide a finite set of choices). For example: A magic string is when you hardcode some special string value directly in your code, instead of giving it a clear, reusable name.

Example without Enum:

if bot_type == "product_bot":   # ← hardcoded magic string
    # do something


Problem: if you mistype "product_bot" (e.g. "productbot") in another place, you wont get an error — it just wont match.

Also, later if you need to rename "product_bot" → "product_recommender", youd have to find and change every string occurrence in your code.

With Enum, you avoid this:

if bot_type == PromptType.PRODUCT_BOT:
    # do something


Now "product_bot" is defined once inside the enum, and the rest of your code refers to it by name (PromptType.PRODUCT_BOT).
class PromptType(str, Enum):

Declares an enumeration class named PromptType.

It inherits from str and Enum:

Inheriting from str makes each enum member also behave like a string (useful for JSON, comparisons, I/O).

Example: PromptType.PRODUCT_BOT.value is 'product_bot'.

When you subclass str + Enum, the enum members are instances that behave like strings in many contexts (e.g., you can often treat them like strings when serializing).
'''
class PromptType(str, Enum):
    PRODUCT_BOT = 'product_bot'

class PromptTemplate:
    def __init__(self, template: str,description: str, version: str='v1' ):
        '''
        Parameters:
            template: str — the template string that contains placeholders like {context}, {question}.
            description: str — a human-readable description of what this template is for.
            version: str='v1' — optional template version (default 'v1').
        '''
        self.template = template.strip()
        self.description = description
        self.version=version

    def format(self, **kwargs) -> str:
        '''
        Defines an instance method to format (fill) the template with actual values.
        **kwargs means you pass named arguments matching the placeholders, e.g. template.format(context="...", question="...").
        Return type hint -> str indicates it returns a formatted string.
        If no placeholders are missing, call the standard Python string .format() to substitute placeholders with values passed in kwargs.
        This returns the final prompt string with {context}, {question}, etc. replaced.
        '''
        missing = [f for f in self.required_placeholders() if f not in kwargs]

        if missing:
            raise ValueError(f"Place holders missing: {missing}")
        return self.template.format(**kwargs)
    
    def required_placeholders(self):
        '''
        A helper method that extracts the placeholder names used in the template.
        Uses string.Formatter().parse(self.template) to break the template into parts.
        Formatter.parse() yields tuples of (literal_text, field_name, format_spec, conversion) for each replacement field in the template.
        Example for "Hello {name}, you have {count} messages" → parse yields segments where field_name will be 'name' and 'count'.
        The list comprehension extracts the field_name for each parsed item, filtering out None / empty values (if field_name) so only named placeholders are returned.
        Result is a list of placeholder names like ['context', 'question'].
        This method is used to check required params before formatting.
        
        Note on the parse() tuple structure: the four values returned are:
        literal_text — the raw text before the replacement field.
        field_name — the name/number in the {...} (e.g., 'context').
        format_spec — optional format specifier after : (e.g., {x:.2f} → .2f).
        conversion — optional conversion (e.g., {x!r} → 'r').
        '''
        return [field_name for _, field_name,_,_ in string.Formatter().parse(self.template) if field_name]
    

##central registry
'''
Declares the registry variable PROMPT_REGISTRY. The : Dict[PromptType, PromptTemplate] is a type hint: the registry maps PromptType keys to PromptTemplate values.
This registry allows lookup of templates by a canonical type enum (safer/better than raw strings).
PromptType.PRODUCT_BOT: PromptTemplate(
Adds an entry keyed by PromptType.PRODUCT_BOT.
Important: the code here is calling PromptTemplate(...) to construct the template instance.
This triple-quoted string is passed as the template argument to PromptTemplate. It contains the prompt text and placeholders {context} and {question} which will be filled later by .format().
)
Closes the PromptTemplate(...) call.
}
Closes the dictionary literal.
'''
PROMPT_REGISTRY: Dict[PromptType, PromptTemplate] = {
    PromptType.PRODUCT_BOT: PromptTemplate(
        """You are an expert EcommerceBot specialized in product recommendations and handling customer 
        queries. Analyse the provided product titles, price, ratings and reviews to provide accurate and 
        helpful responses. Stay relevant to the context, and keep your answers concise and informative. 

        CONTEXT:
        {context}

        QUESTION:
        {question}

        """,
        description= 'Handles ecommerce QnA.'

    )
}