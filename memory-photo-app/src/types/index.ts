export type GroupType = '母婴' | '家庭' | '毕业' | '追思' | '朋友' | '其他';

export interface StylePrompt {
  key: string;
  label: string;
  prompt: string;
}

export interface ProcessStatus {
  groupId: string;
  step: number;
  done: boolean;
}
