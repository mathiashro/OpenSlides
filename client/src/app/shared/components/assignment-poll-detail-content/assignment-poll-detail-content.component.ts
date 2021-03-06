import { Component, Input } from '@angular/core';

import { AssignmentPollMethod } from 'app/shared/models/assignments/assignment-poll';
import { ViewAssignmentPoll } from 'app/site/assignments/models/view-assignment-poll';
import { AssignmentPollService } from 'app/site/assignments/modules/assignment-poll/services/assignment-poll.service';
import { PollData, PollTableData, VotingResult } from 'app/site/polls/services/poll.service';

@Component({
    selector: 'os-assignment-poll-detail-content',
    templateUrl: './assignment-poll-detail-content.component.html',
    styleUrls: ['./assignment-poll-detail-content.component.scss']
})
export class AssignmentPollDetailContentComponent {
    @Input()
    public poll: ViewAssignmentPoll | PollData;

    public constructor(private pollService: AssignmentPollService) {}

    private get method(): string {
        return this.poll.pollmethod;
    }

    public get showYHeader(): boolean {
        return this.isMethodY || this.isMethodYN || this.isMethodYNA;
    }

    public get showNHeader(): boolean {
        return this.isMethodN || this.isMethodYN || this.isMethodYNA;
    }

    public get isMethodY(): boolean {
        return this.method === AssignmentPollMethod.Y;
    }

    public get isMethodN(): boolean {
        return this.method === AssignmentPollMethod.N;
    }

    public get isMethodYN(): boolean {
        return this.method === AssignmentPollMethod.YN;
    }

    public get isMethodYNA(): boolean {
        return this.method === AssignmentPollMethod.YNA;
    }

    public get tableData(): PollTableData[] {
        return this.pollService.generateTableData(this.poll);
    }

    public getVoteClass(votingResult: VotingResult): string {
        const votingClass = votingResult.vote;
        if (this.isMethodN && votingClass === 'no') {
            return 'yes';
        } else {
            return votingClass;
        }
    }

    public filterRelevantResults(votingResult: VotingResult[]): VotingResult[] {
        return votingResult.filter(result => {
            return result && this.voteFitsMethod(result);
        });
    }

    public getVoteAmount(vote: VotingResult, row: PollTableData): number {
        if (this.isMethodN && row.class === 'user') {
            if (vote.amount < 0) {
                return vote.amount;
            } else {
                return this.poll.votesvalid - vote.amount;
            }
        } else {
            return vote.amount;
        }
    }

    public voteFitsMethod(result: VotingResult): boolean {
        if (!result.vote) {
            return true;
        }
        if (this.isMethodY) {
            return result.vote === 'yes';
        } else if (this.isMethodN) {
            return result.vote === 'no';
        } else if (this.isMethodYN) {
            return result.vote !== 'abstain';
        } else {
            return true;
        }
    }
}
