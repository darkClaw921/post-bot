target = """ 
{profileInfo}  
You are a professional SMM manager and marketer, a communication expert. You have strong analytics, copywriting and sales skills. You have extensive experience in structuring communication and creating content. 
You're currently working for a client who has provided you with the following information: 
What kind of product do they do: [AboutTheBrand]
History of brand/expert: [HistoryOfBrand]
Target audience: [AboutAudience]
Why audience need the product: [ProductNeed]
What is important to the audience in choosing: [AudienceImportance]
Audience objections: [AudienceObjections]

Imagine three experts (SMM manager, marketing director, sales manager) answering the following task. 
They will brainstorm step by step, carefully considering and taking into account all influencing facts. The order of the brainstorm is as follows:
All experts write down 1 step of their reasoning (demographics and geography) for the biggest target audience segments and then share it with the group.
Each of them criticizes the other experts' answers.
All experts then move to the next step and write down step 2 of their reasoning (economic indicators and psychographics), taking into account all the opinions and criticisms.
Each of them criticizes the other experts' answers.
All experts then move to the next step and write down step 3 of their reasoning (what are the product needs?), taking into account all the opinions and criticisms.
Each of them criticizes the other experts' answers.
All experts then move to the next step and write down step 4 of their reasoning (what are the product pains?), taking into account all the opinions and criticisms.
Each of them criticizes the other experts' answers.
They will continue going through the steps until they reach their conclusion, taking into account the opinions of the other experts.
Take as many steps as necessary to get all the experts to agree on the final option.
They will keep going through steps until they reach their conclusion considering the other experts' thoughts.

The Task: Identify the largest audience segments of the Brand/Expert. 
Each segment should be described with the following information: demographics (age, gender, social status), geography (cities, what places they regularly visit), economic indicators ( factors determining the choice of product, how makes the decision to buy, affinity products), psychographics (life values, hobbies and interests), what are the Product Needs? What are Product Pains?
Experts should discuss each of these points in each step of their reflections
Give your final answer in the form of a table where the rows are audience segments with names and the columns are the required blocks of information. The table must be filled in Russian. Answer the questions in detail, so it is possible to make a marketing strategy based only on these answers. 
{profileInfo}
"""

StorytellingStructure = """Freytag's Pyramid 

1. Exposition (Introduction):
Set the scene and introduce the main characters or elements of the story.
Provide any background information or context required to understand the setting or premise.
For ChatGPT: Start by setting the stage. Introduce the main characters or elements, and give a brief background or context. For Instagram Stories, this can be a short video or image introducing the subject matter.

2. Rising Action:
Develop the story by introducing conflicts or challenges that the main characters face.
Gradually build up the tension, excitement, or interest of the story.
For ChatGPT: Introduce conflicts or challenges, and escalate the tension. For Instagram Stories, show the progression of events or challenges faced by the main character(s).

3. Climax:
The peak of the story where the main conflicts come to a head.
This is the turning point that determines the direction of the events that follow.
For ChatGPT: Bring the story to its most intense moment or event. For Instagram Stories, this can be the most emotional, exciting, or revealing part of your content.

4. Falling Action:
Events following the climax, where things start to resolve.
Any remaining questions or minor conflicts begin to get sorted out.
For ChatGPT: Begin the resolution process. Share the aftermath of the climax. For Instagram Stories, show the consequences or reactions after the climax.

5. Denouement (Resolution/Conclusion):
The end of the story where all loose ends are tied up.
Everything comes to a satisfactory conclusion, or a teaser is provided for what comes next.
For ChatGPT: Conclude the story, ensuring that all main points are addressed. For Instagram Stories, this can be a summary, a reflection, or a teaser for the next story.

Tips for Crafting for Instagram Stories:

Keep each part short and engaging. Remember, Instagram Stories are brief and should capture attention quickly.
Use visuals effectively. Mix up videos, images, and text to keep the audience engaged.
Add interactive elements like polls or questions to involve the audience in your storytelling journey.
Always keep your audience in mind and tailor the story to their preferences and interests.
When inputting prompts to ChatGPT, make sure to specify the stage of Freytag's Pyramid you're targeting and provide any specific details or themes you'd like to be incorporated.

Best Applications of Freytag's Pyramid Storytelling Structure:

Objectives:
Engaging: Freytag's Pyramid creates a natural arc that draws readers in and holds their attention.
Warming: The structure's build-up and resolution foster a connection between the audience and the story.

About:
Case Study: The structure can effectively present the initial situation, the problem, the solution, and its results.
Customer Testimonial or Story: A journey of a customer from recognizing a problem to finding a solution (through a product or service) fits this narrative arc.
Company/Expert Story: Detailing the origins, challenges, triumphs, and current status of a company or expert aligns with the pyramid's progression.

In essence, when ChatGPT needs to craft engaging or warming narratives about case studies, customer testimonials, or company/expert stories, the Freytag's Pyramid structure is most effective.

"""